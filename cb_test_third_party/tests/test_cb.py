# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo.addons.cb_test.tests.test_cb import TestCB
from odoo.tests.common import at_install, post_install


@post_install(True)
@at_install(False)
class TestCBThirdParty(TestCB):
    def test_performer(self):
        self.plan_definition2.write(
            {"third_party_bill": False, "performer_required": True}
        )
        self.env["workflow.plan.definition.action"].create(
            {
                "activity_definition_id": self.activity5.id,
                "direct_plan_definition_id": self.plan_definition2.id,
                "is_billable": False,
                "name": "Action",
                "performer_id": self.practitioner_02.id,
            }
        )
        encounter = self.env["medical.encounter"].create(
            {"patient_id": self.patient_01.id, "center_id": self.center.id}
        )
        careplan_wizard = (
            self.env["medical.encounter.add.careplan"]
            .with_context(default_encounter_id=encounter.id)
            .new({"coverage_id": self.coverage_01.id})
        )
        careplan_wizard.onchange_coverage()
        careplan_wizard.onchange_coverage_template()
        careplan_wizard.onchange_payor()
        careplan_wizard = careplan_wizard.create(
            careplan_wizard._convert_to_write(careplan_wizard._cache)
        )
        self.assertEqual(encounter, careplan_wizard.encounter_id)
        self.assertEqual(encounter.center_id, careplan_wizard.center_id)
        careplan_wizard.run()
        careplan = encounter.careplan_ids
        self.assertEqual(careplan.center_id, encounter.center_id)
        wizard = self.env["medical.careplan.add.plan.definition"].create(
            {
                "careplan_id": careplan.id,
                "agreement_line_id": self.agreement_line3.id,
                "performer_id": self.practitioner_01.id,
            }
        )
        self.assertIn(self.agreement, wizard.agreement_ids)
        self.action.is_billable = False
        wizard.run()
        group = self.env["medical.request.group"].search(
            [("careplan_id", "=", careplan.id)]
        )
        group.ensure_one()
        self.assertEqual(group.center_id, encounter.center_id)
        self.assertEqual(group.performer_id, self.practitioner_01)
        self.assertEqual(len(group.procedure_request_ids.ids), 2)
        self.assertTrue(
            group.procedure_request_ids.filtered(
                lambda r: r.performer_id == self.practitioner_01
            )
        )
        self.assertTrue(
            group.procedure_request_ids.filtered(
                lambda r: r.performer_id == self.practitioner_02
            )
        )

    def test_down_payments_third_party(self):
        self.plan_definition2.third_party_bill = True
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line3
        )
        self.env["wizard.medical.encounter.add.amount"].create(
            {
                "encounter_id": encounter.id,
                "pos_session_id": self.session.id,
                "journal_id": self.journal_1[0].id,
                "amount": 100,
            }
        ).run()
        for request in group.procedure_request_ids:
            request.draft2active()
            self.assertEqual(request.center_id, encounter.center_id)
            procedure = request.generate_event()
            procedure.performer_id = self.practitioner_01
            procedure.commission_agent_id = self.practitioner_01
            procedure.performer_id = self.practitioner_02
            procedure._onchange_performer_id()
            self.assertEqual(
                procedure.commission_agent_id, self.practitioner_02
            )
        self.practitioner_02.third_party_sequence_id = self.env[
            "ir.sequence"
        ].create({"name": "sequence"})
        self.env["wizard.medical.encounter.close"].create(
            {"encounter_id": encounter.id, "pos_session_id": self.session.id}
        ).run()
        self.assertEqual(encounter.pending_private_amount, 0)
        extra_order = encounter.sale_order_ids.filtered(
            lambda r: r.is_down_payment and r.state == "draft"
        )
        self.env["wizard.medical.encounter.finish"].create(
            {
                "encounter_id": encounter.id,
                "pos_session_id": self.session.id,
                "journal_id": self.journal_1[0].id,
            }
        ).run()
        sale_order = encounter.sale_order_ids.filtered(
            lambda r: not r.is_down_payment and not r.third_party_partner_id
        )
        self.assertTrue(sale_order)
        self.assertEqual(sum(s.amount_total for s in sale_order), 0)
        payments = sale_order.mapped("invoice_ids.bank_statement_line_ids")
        self.assertFalse(payments)
        payments = extra_order.mapped("invoice_ids.bank_statement_line_ids")
        self.assertTrue(payments)
        self.assertEqual(-100, sum(p.amount for p in payments))
        sale_order = encounter.sale_order_ids.filtered(
            lambda r: not r.is_down_payment and r.third_party_partner_id
        )
        self.assertTrue(sale_order)
        payments = sale_order.mapped("bank_statement_line_ids")
        self.assertTrue(payments)
        self.assertEqual(100, sum(p.amount for p in payments))
        self.assertEqual(sum(s.amount_total for s in sale_order), 100)

    def test_third_party(self):
        self.plan_definition.is_breakdown = True
        self.plan_definition.is_billable = True
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line3
        )
        self.assertEqual(encounter.sale_order_count, 0)
        self.assertTrue(group.procedure_request_ids)
        for request in group.procedure_request_ids:
            request.draft2active()
            self.assertEqual(request.center_id, encounter.center_id)
            procedure = request.generate_event()
            procedure.performer_id = self.practitioner_01
            procedure.commission_agent_id = self.practitioner_01
            procedure.performer_id = self.practitioner_02
            procedure._onchange_performer_id()
            self.assertEqual(
                procedure.commission_agent_id, self.practitioner_02
            )
        self.practitioner_02.third_party_sequence_id = self.env[
            "ir.sequence"
        ].create({"name": "sequence"})
        self.assertTrue(
            group.is_sellable_insurance or group.is_sellable_private
        )
        self.assertTrue(group.third_party_bill)
        self.env["wizard.medical.encounter.close"].create(
            {"encounter_id": encounter.id, "pos_session_id": self.session.id}
        ).run()
        self.assertGreater(encounter.sale_order_count, 0)
        self.assertTrue(encounter.sale_order_ids)
        self.assertFalse(encounter.has_preinvoicing)
        sale_order = encounter.sale_order_ids
        self.assertTrue(sale_order.third_party_order)
        self.assertEqual(
            sale_order.third_party_partner_id, self.practitioner_02
        )
        self.assertGreater(encounter.pending_private_amount, 0)
        journal = self.session.statement_ids.mapped("journal_id")[0]
        self.env["wizard.medical.encounter.finish"].create(
            {
                "encounter_id": encounter.id,
                "pos_session_id": self.session.id,
                "journal_id": journal.id,
            }
        ).run()
        self.assertFalse(sale_order.invoice_ids)
        self.assertEqual(encounter.pending_private_amount, 0)
        self.session.action_pos_session_approve()
