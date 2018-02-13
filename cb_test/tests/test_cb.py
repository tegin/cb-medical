# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestMedicalCareplanSale(TransactionCase):
    def setUp(self):
        super(TestMedicalCareplanSale, self).setUp()
        self.payor = self.env['res.partner'].create({
            'name': 'Payor',
            'is_payor': True,
        })
        self.sub_payor = self.env['res.partner'].create({
            'name': 'Sub Payor',
            'is_sub_payor': True,
            'payor_id': self.payor.id,
        })
        self.coverage_template = self.env['medical.coverage.template'].create({
            'payor_id': self.payor.id,
            'name': 'Coverage',
        })
        self.company = self.browse_ref('base.main_company')
        self.location = self.env['res.partner'].create({
            'name': 'Location',
            'is_location': True,
            'stock_location_id': self.browse_ref('stock.warehouse0').id
        })
        self.agreement = self.env['medical.coverage.agreement'].create({
            'name': 'Agreement',
            'location_ids': [(4, self.location.id)],
            'coverage_template_ids': [(4, self.coverage_template.id)],
            'company_id': self.company.id,
            'invoice_group_method_id': self.browse_ref(
                'cb_medical_sale_invoice_group_method.by_preinvoicing').id
        })
        self.patient_01 = self.create_patient('Patient 01')
        self.coverage_01 = self.env['medical.coverage'].create({
            'patient_id': self.patient_01.id,
            'coverage_template_id': self.coverage_template.id,
        })
        self.product_01 = self.create_product('Medical ressonance')
        self.product_02 = self.create_product('Report')
        self.product_03 = self.env['product.product'].create({
            'type': 'consu',
            'name': 'Clinical material',
            'is_medication': True,
            'lst_price': 10.0,
        })
        self.product_03.qty_available = 50.0
        self.type = self.browse_ref('medical_workflow.medical_workflow')
        self.type.model_ids = [(4, self.browse_ref(
            'medical_medication_request.model_medical_medication_request').id)]
        self.plan_definition = self.env['workflow.plan.definition'].create({
            'name': 'Plan',
            'type_id': self.type.id,
            'is_billable': True,
        })
        self.activity = self.env['workflow.activity.definition'].create({
            'name': 'Activity',
            'service_id': self.product_02.id,
            'model_id': self.browse_ref('medical_clinical_procedure.'
                                        'model_medical_procedure_request').id,
            'type_id': self.type.id,
        })
        self.activity2 = self.env['workflow.activity.definition'].create({
            'name': 'Activity2',
            'service_id': self.product_03.id,
            'model_id': self.browse_ref('medical_medication_request.'
                                        'model_medical_medication_request').id,
            'type_id': self.type.id,
        })
        self.action = self.env['workflow.plan.definition.action'].create({
            'activity_definition_id': self.activity.id,
            'direct_plan_definition_id': self.plan_definition.id,
            'is_billable': True,
            'name': 'Action',
        })
        self.action2 = self.env['workflow.plan.definition.action'].create({
            'activity_definition_id': self.activity2.id,
            'direct_plan_definition_id': self.plan_definition.id,
            'is_billable': True,
            'name': 'Action2',
        })
        self.agreement_line = self.env[
            'medical.coverage.agreement.item'
        ].create({
            'product_id': self.product_01.id,
            'coverage_agreement_id': self.agreement.id,
            'plan_definition_id': self.plan_definition.id,
            'total_price': 100,
            'coverage_percentage': 0.5
        })
        self.agreement_line2 = self.env[
            'medical.coverage.agreement.item'
        ].create({
            'product_id': self.product_03.id,
            'coverage_agreement_id': self.agreement.id,
            'total_price': 0.0,
            'coverage_percentage': 100.0,
        })
        self.practitioner_01 = self.create_practitioner('Practitioner 01')
        self.practitioner_02 = self.create_practitioner('Practitioner 02')
        self.product_01.medical_commission = True
        self.action.fixed_fee = 1
        self.pos_config = self.env['pos.config'].create({'name': 'PoS config'})
        self.pos_config.open_session_cb()
        self.session = self.pos_config.current_session_id
        self.session.action_pos_session_open()
        param_obj = self.env['ir.config_parameter'].sudo()
        param = param_obj.get_param('sale.default_deposit_product_id', False)
        if not param:
            param_obj.set_param(
                'sale.default_deposit_product_id',
                self.create_product('Down payment').id
            )

    def create_patient(self, name):
        return self.env['medical.patient'].create({
            'name': name
        })

    def create_product(self, name):
        return self.env['product.product'].create({
            'type': 'service',
            'name': name,
        })

    def create_practitioner(self, name):
        return self.env['res.partner'].create({
            'name': name,
            'is_practitioner': True,
            'agent': True,
            'commission': self.browse_ref(
                'cb_medical_commission.commission_01').id,
        })

    def create_careplan_and_group(self):
        careplan = self.env['medical.careplan'].create({
            'patient_id': self.patient_01.id,
            'coverage_id': self.coverage_01.id,
        })
        wizard = self.env['medical.careplan.add.plan.definition'].create({
            'careplan_id': careplan.id,
            'agreement_line_id': self.agreement_line.id,
        })
        self.action.is_billable = False
        wizard.run()
        group = self.env['medical.request.group'].search([
            ('careplan_id', '=', careplan.id)])
        group.ensure_one()
        return careplan, group

    def test_careplan_sale(self):
        encounter = self.env['medical.encounter'].create({
            'patient_id': self.patient_01.id,
            'location_id': self.location.id,
        })
        encounter_02 = self.env['medical.encounter'].create({
            'patient_id': self.patient_01.id,
            'location_id': self.location.id,
        })
        careplan = self.env['medical.careplan'].create({
            'patient_id': self.patient_01.id,
            'encounter_id': encounter.id,
            'coverage_id': self.coverage_01.id,
            'sub_payor_id': self.sub_payor.id,
        })
        self.env['wizard.medical.careplan.add.amount'].create({
            'careplan_id': careplan.id,
            'amount': 10,
            'pos_session_id': self.session.id,
            'journal_id': self.session.journal_ids[0].id,
        }).run()
        wizard = self.env['medical.careplan.add.plan.definition'].create({
            'careplan_id': careplan.id,
            'agreement_line_id': self.agreement_line.id,
        })
        with self.assertRaises(ValidationError):
            wizard.run()
        self.action.is_billable = False
        wizard.run()
        groups = self.env['medical.request.group'].search([
            ('careplan_id', '=', careplan.id)])
        self.assertTrue(groups)
        medication_requests = self.env['medical.medication.request'].search([
            ('careplan_id', '=', careplan.id)
        ])
        for request in medication_requests:
            request.qty = 2
            request.draft2active()
            values = request.action_view_medication_administration()['context']
            admin = self.env[
                'medical.medication.administration'].with_context(
                values).create({})
            admin.location_id = self.location.id
            admin.preparation2in_progress()
            admin.in_progress2completed()
            stock_move = self.env['stock.move.line'].search([
                ('product_id', '=', self.product_03.id),
                ('medication_administration_id', '=', admin.id)
            ])
            self.assertEqual(stock_move.qty_done, 2.0)
        self.env['wizard.medical.careplan.close'].create({
            'careplan_id': careplan.id,
            'pos_session_id': self.session.id,
        }).run()
        self.assertGreater(len(careplan.sale_order_ids), 0)
        self.session.action_pos_session_closing_control()
        self.assertTrue(self.session.invoice_ids)
        self.assertTrue(self.session.down_payment_ids)
        self.assertEqual(self.session.validation_status, 'in_progress')
        procedure_requests = self.env['medical.procedure.request'].search([
            ('careplan_id', '=', careplan.id)
        ])
        self.assertGreater(len(procedure_requests), 0)
        medication_requests = self.env['medical.medication.request'].search([
            ('careplan_id', '=', careplan.id)
        ])
        self.assertGreater(len(medication_requests), 0)
        for sale_order in careplan.sale_order_ids:
            sale_order.recompute_lines_agents()
            self.assertEqual(sale_order.commission_total, 0)
            medicaments = self.env['sale.order.line'].search([
                ('order_id', '=', sale_order.id),
                ('product_id', '=', self.product_03.id),
            ])
            for medicament in medicaments:
                medicament_price = medicament.price_unit
                self.assertEqual(medicament_price, 20.0)
        procedure_requests = self.env['medical.procedure.request'].search([
            ('careplan_id', '=', careplan.id)
        ])
        self.assertGreater(len(procedure_requests), 0)
        for request in procedure_requests:
            procedure = request.generate_event()
            procedure.performer_id = self.practitioner_01
            procedure.commission_agent_id = self.practitioner_01
            procedure.performer_id = self.practitioner_02
            procedure._onchange_performer_id()
            self.assertEqual(
                procedure.commission_agent_id, self.practitioner_02)
        careplan.recompute_commissions()
        for sale_order in careplan.sale_order_ids:
            sale_order.recompute_lines_agents()
            self.assertGreater(sale_order.commission_total, 0)
        preinvoice_obj = self.env['sale.preinvoice.group']
        self.assertFalse(preinvoice_obj.search([
            ('agreement_id', '=', self.agreement.id)]))
        self.env['wizard.sale.preinvoice.group'].create({
            'company_ids': [(6, 0, self.company.ids)],
            'payor_ids': [(6, 0, self.payor.ids)]
        }).run()
        self.assertFalse(preinvoice_obj.search([
            ('agreement_id', '=', self.agreement.id)]))
        for sale_order in careplan.sale_order_ids:
            sale_order.action_confirm()
        self.env['wizard.sale.preinvoice.group'].create({
            'company_ids': [(6, 0, self.company.ids)],
            'payor_ids': [(6, 0, self.payor.ids)]
        }).run()
        preinvoices = preinvoice_obj.search([
            ('agreement_id', '=', self.agreement.id),
            ('state', '=', 'draft')
        ])
        self.assertTrue(preinvoices)
        # Test cancellation of preinvoices
        for preinvoice in preinvoices:
            self.assertFalse(preinvoice.validated_line_ids)
            preinvoice.cancel()
            self.assertFalse(preinvoice.line_ids)
        preinvoices = preinvoice_obj.search([
            ('agreement_id', '=', self.agreement.id),
            ('state', '=', 'draft')
        ])
        self.assertFalse(preinvoices)
        self.env['wizard.sale.preinvoice.group'].create({
            'company_ids': [(6, 0, self.company.ids)],
            'payor_ids': [(6, 0, self.payor.ids)]
        }).run()
        preinvoices = preinvoice_obj.search([
            ('agreement_id', '=', self.agreement.id),
            ('state', '=', 'draft')
        ])
        self.assertTrue(preinvoices)
        # Test unlink of not validated order_lines
        for preinvoice in preinvoices:
            self.assertTrue(preinvoice.non_validated_line_ids)
            self.assertFalse(preinvoice.validated_line_ids)
            preinvoice.start()
            preinvoice.close_sorting()
            self.assertTrue(preinvoice.non_validated_line_ids)
            preinvoice.close()
            self.assertFalse(preinvoice.non_validated_line_ids)
        preinvoices = preinvoice_obj.search([
            ('agreement_id', '=', self.agreement.id),
            ('state', '=', 'draft')
        ])
        self.assertFalse(preinvoices)
        self.env['wizard.sale.preinvoice.group'].create({
            'company_ids': [(6, 0, self.company.ids)],
            'payor_ids': [(6, 0, self.payor.ids)]
        }).run()
        preinvoices = preinvoice_obj.search([
            ('agreement_id', '=', self.agreement.id),
            ('state', '=', 'draft')
        ])
        self.assertTrue(preinvoices)
        invoice_obj = self.env['account.invoice']
        self.assertFalse(invoice_obj.search([
            ('partner_id', '=', self.payor.id)
        ]))
        # Test barcodes
        for preinvoice in preinvoices:
            self.assertFalse(preinvoice.validated_line_ids)
            preinvoice.start()
            barcode = self.env['wizard.sale.preinvoice.group.barcode'].create({
                'preinvoice_group_id': preinvoice.id,
            })
            barcode.on_barcode_scanned(encounter.internal_identifier)
            self.assertEqual(barcode.status_state, 0)
            barcode.on_barcode_scanned('No Barcode')
            self.assertEqual(barcode.status_state, 1)
            barcode.on_barcode_scanned(encounter_02.internal_identifier)
            self.assertEqual(barcode.status_state, 1)
            preinvoice.close_sorting()
            preinvoice.close()
            self.assertTrue(preinvoice.invoice_id)
        invoices = invoice_obj.search([
            ('partner_id', 'in', [self.payor.id, self.sub_payor.id])
        ])
        self.assertTrue(invoices)
        # Test invoice unlink
        for invoice in invoices:
            self.assertEqual(invoice.state, 'draft')
            invoice.invoice_line_ids.unlink()
        for sale_order in careplan.sale_order_ids:
            for line in sale_order.order_line:
                self.assertFalse(line.preinvoice_group_id)
        # Test manual validation of lines on preinvoices
        preinvoices = preinvoice_obj.search([
            ('agreement_id', '=', self.agreement.id),
            ('state', '=', 'draft')
        ])
        self.assertFalse(preinvoices)
        self.env['wizard.sale.preinvoice.group'].create({
            'company_ids': [(6, 0, self.company.ids)],
            'payor_ids': [(6, 0, self.payor.ids)]
        }).run()
        preinvoices = preinvoice_obj.search([
            ('agreement_id', '=', self.agreement.id),
            ('state', '=', 'draft')
        ])
        self.assertTrue(preinvoices)
        for preinvoice in preinvoices:
            self.assertFalse(preinvoice.validated_line_ids)
            preinvoice.start()
            for line in preinvoice.line_ids:
                line.validate_line()
            preinvoice.close_sorting()
            preinvoice.close()
            self.assertTrue(preinvoice.line_ids)
            self.assertTrue(preinvoice.invoice_id)
        invoices = invoice_obj.search([
            ('partner_id', 'in', [self.payor.id, self.sub_payor.id])
        ])
        self.assertTrue(invoices)
        for invoice in invoices:
            self.assertGreater(invoice.commission_total, 0)
            invoice.recompute_lines_agents()
            self.assertGreater(invoice.commission_total, 0)

    def test_no_agreement(self):
        self.plan_definition.is_breakdown = True
        self.plan_definition.is_billable = True
        careplan, group = self.create_careplan_and_group()
        self.assertTrue(group.is_billable)
        self.assertTrue(group.is_breakdown)
        with self.assertRaises(ValidationError):
            group.breakdown()

    def test_no_breakdown(self):
        self.plan_definition.is_billable = True
        self.plan_definition.is_breakdown = False
        careplan, group = self.create_careplan_and_group()
        self.assertTrue(group.is_billable)
        self.assertFalse(group.is_breakdown)
        with self.assertRaises(ValidationError):
            group.breakdown()

    def test_correct(self):
        self.plan_definition.is_breakdown = True
        self.plan_definition.is_billable = True
        careplan, group = self.create_careplan_and_group()
        self.assertTrue(group.is_billable)
        self.assertTrue(group.is_breakdown)
        self.env[
            'medical.coverage.agreement.item'
        ].create({
            'product_id': self.product_02.id,
            'coverage_agreement_id': self.agreement.id,
            'total_price': 110,
            'coverage_percentage': 0.5
        })
        group.breakdown()
        self.assertFalse(group.is_billable)
        self.assertFalse(group.is_breakdown)
        self.env['wizard.medical.careplan.close'].create({
            'careplan_id': careplan.id,
            'pos_session_id': self.session.id,
        }).run()
        self.assertGreater(len(careplan.sale_order_ids), 0)
