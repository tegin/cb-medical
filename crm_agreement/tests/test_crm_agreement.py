# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestCrmAgreement(TransactionCase):
    def setUp(self):
        super(TestCrmAgreement, self).setUp()
        self.payor = self.env["res.partner"].create(
            {
                "name": "Payor",
                "is_medical": True,
                "is_payor": True,
                "email": "payor@email.com",
            }
        )
        self.contact = self.env["res.partner"].create(
            {"name": "Contact", "parent_id": self.payor.id}
        )
        self.template_1 = self.env["medical.coverage.template"].create(
            {"payor_id": self.payor.id, "name": "Template 01"}
        )
        self.template_2 = self.env["medical.coverage.template"].create(
            {"payor_id": self.payor.id, "name": "Template 02"}
        )
        self.company = self.browse_ref("base.main_company")
        self.center = self.env["res.partner"].create(
            {"name": "Center", "is_center": True, "is_medical": True}
        )
        self.method = self.env["medical.authorization.method"].create(
            {"name": "Test method", "code": "TEST"}
        )
        self.format = self.env["medical.authorization.format"].create(
            {"name": "Test format", "code": "test"}
        )

    def test_lead_to_agreement(self):
        partner = self.contact
        lead = self.env["crm.lead"].create(
            {"partner_id": partner.id, "name": "TEST LEAD"}
        )
        self.assertFalse(lead.agreement_ids)
        self.assertEqual(0, lead.agreement_count)
        agreement_action = lead.view_agreements()
        self.assertFalse(agreement_action.get("res_id", False))
        self.assertFalse(
            self.env["medical.coverage.agreement"].search(
                agreement_action.get("domain", [])
            )
        )
        agreement = (
            self.env["medical.coverage.agreement"]
            .with_context(**agreement_action.get("context", {}))
            .create(
                {
                    "name": "Test agreement",
                    "center_ids": [(4, self.center.id)],
                    "company_id": self.company.id,
                    "authorization_method_id": self.method.id,
                    "authorization_format_id": self.format.id,
                }
            )
        )
        agreement.refresh()
        self.assertIn(self.template_1, agreement.coverage_template_ids)
        self.assertIn(self.template_2, agreement.coverage_template_ids)
        self.assertIn(lead, agreement.lead_ids)
        self.assertIn(agreement, lead.agreement_ids)
        self.assertEqual(1, lead.agreement_count)
        agreement_action = lead.view_agreements()
        self.assertEqual(agreement_action.get("res_id", False), agreement.id)
        self.assertIn(
            agreement,
            self.env["medical.coverage.agreement"].search(
                agreement_action.get("domain", [])
            ),
        )
        agreement2 = (
            self.env["medical.coverage.agreement"]
            .with_context(**agreement_action.get("context", {}))
            .create(
                {
                    "name": "Test agreement",
                    "center_ids": [(4, self.center.id)],
                    "company_id": self.company.id,
                    "authorization_method_id": self.method.id,
                    "authorization_format_id": self.format.id,
                }
            )
        )
        self.assertIn(self.template_1, agreement2.coverage_template_ids)
        self.assertIn(self.template_2, agreement2.coverage_template_ids)
        self.assertIn(lead, agreement2.lead_ids)
        lead.refresh()
        self.assertIn(agreement2, lead.agreement_ids)
        self.assertEqual(2, lead.agreement_count)
        agreement_action = lead.view_agreements()
        self.assertFalse(agreement_action.get("res_id", False))
        agreements = self.env["medical.coverage.agreement"].search(
            agreement_action.get("domain", [])
        )
        self.assertIn(agreement, agreements)
        self.assertIn(agreement2, agreements)

    def test_agreement_to_lead(self):
        agreement = self.env["medical.coverage.agreement"].create(
            {
                "name": "Test agreement",
                "center_ids": [(4, self.center.id)],
                "company_id": self.company.id,
                "authorization_method_id": self.method.id,
                "authorization_format_id": self.format.id,
                "coverage_template_ids": [
                    (4, self.template_1.id),
                    (4, self.template_2.id),
                ],
            }
        )
        self.assertEqual(0, agreement.lead_count)
        self.assertFalse(agreement.lead_ids)
        lead_action = agreement.view_leads()
        self.assertFalse(lead_action.get("res_id", False))
        self.assertFalse(
            self.env["crm.lead"].search(lead_action.get("domain", []))
        )
        obj = self.env["crm.lead"].with_context(
            **lead_action.get("context", {})
        )

        lead = obj.create({"name": "Test LEAD"})
        self.assertIn(agreement, lead.agreement_ids)
        self.assertEqual(lead.partner_id, self.payor)
        self.assertEqual(1, agreement.lead_count)
        self.assertIn(lead, agreement.lead_ids)
        lead_action = agreement.view_leads()
        self.assertEqual(lead_action.get("res_id", False), lead.id)
        self.assertIn(
            lead, self.env["crm.lead"].search(lead_action.get("domain", []))
        )
        lead2 = (
            self.env["crm.lead"]
            .with_context(**lead_action.get("context", {}))
            .create({"name": "Test LEAD"})
        )
        self.assertEqual(lead2.partner_id, self.payor)
        self.assertIn(agreement, lead2.agreement_ids)
        agreement.refresh()
        self.assertEqual(2, agreement.lead_count)
        self.assertIn(lead, agreement.lead_ids)
        self.assertIn(lead2, agreement.lead_ids)
        lead_action = agreement.view_leads()
        self.assertFalse(lead_action.get("res_id", False))
        leads = self.env["crm.lead"].search(lead_action.get("domain", []))
        self.assertIn(lead, leads)
        self.assertIn(lead2, leads)

    def test_lead_onchange(self):
        agreement = self.env["medical.coverage.agreement"].create(
            {
                "name": "Test agreement",
                "center_ids": [(4, self.center.id)],
                "company_id": self.company.id,
                "authorization_method_id": self.method.id,
                "authorization_format_id": self.format.id,
                "coverage_template_ids": [
                    (4, self.template_1.id),
                    (4, self.template_2.id),
                ],
            }
        )
        lead = self.env["crm.lead"].new(
            {
                "name": "Test",
                "partner_id": self.payor.id,
                "agreement_ids": [(6, 0, agreement.ids)],
            }
        )
        lead.partner_id = self.contact
        lead._onchange_partner_id_values(lead.partner_id.id)
        self.assertIn(agreement.id, lead.agreement_ids.ids)
        payor2 = self.env["res.partner"].create(
            {"name": "Payor2", "is_medical": True, "is_payor": True}
        )
        lead.partner_id = payor2
        lead._onchange_partner_id()
        self.assertNotIn(agreement, lead.agreement_ids)

    def test_lead_add_agreement(self):
        agreement = self.env["medical.coverage.agreement"].create(
            {
                "name": "Test agreement",
                "center_ids": [(4, self.center.id)],
                "company_id": self.company.id,
                "authorization_method_id": self.method.id,
                "authorization_format_id": self.format.id,
                "coverage_template_ids": [
                    (4, self.template_1.id),
                    (4, self.template_2.id),
                ],
            }
        )
        lead = self.env["crm.lead"].create(
            {"name": "Test", "partner_id": self.payor.id}
        )
        wizard = self.env["crm.lead.add.agreement"].create(
            {"lead_id": lead.id, "agreement_id": agreement.id}
        )
        wizard.link_to_existing()
        lead.refresh()
        agreement.refresh()
        self.assertIn(lead, agreement.lead_ids)
        self.assertIn(agreement, lead.agreement_ids)

        agreements_count_before = len(
            self.env["medical.coverage.agreement"].search([])
        )
        wizard.generate_new()
        lead.refresh()
        agreements_count_after = len(
            self.env["medical.coverage.agreement"].search([])
        )
        self.assertEqual(agreements_count_before + 1, agreements_count_after)

    def test_view_quote(self):
        lead = self.env["crm.lead"].create(
            {"name": "Test", "partner_id": self.payor.id}
        )
        self.assertEqual(lead.medical_quote_count, 0)
        action = lead.view_medical_quotes()
        quote = (
            self.env["medical.quote"]
            .with_context(**action["context"])
            .create(
                {
                    "coverage_template_id": self.template_1.id,
                    "center_id": self.center.id,
                }
            )
        )
        self.assertEqual(lead, quote.lead_id)
        lead.refresh()
        self.assertEqual(1, lead.medical_quote_count)
        action = lead.view_medical_quotes()
        self.assertTrue(quote.id, action["res_id"])

    def test_generate_quote(self):
        lead = self.env["crm.lead"].create(
            {"name": "Test", "partner_id": self.payor.id}
        )
        self.assertEqual(lead.medical_quote_count, 0)
        action = lead.generate_quote()

        quote = self.env[action.get("res_model")].browse(action.get("res_id"))
        self.assertEqual("medical.quote", quote._name)
        self.assertEqual(lead.id, action["context"]["default_lead_id"])
        self.assertEqual(
            lead.partner_id.id, action["context"]["default_payor_id"]
        )

    def test_send_email(self):
        lead = self.env["crm.lead"].create(
            {"name": "Test", "partner_id": self.payor.id}
        )
        action = lead.send_email_from_lead()
        email = self.env[action.get("res_model")].browse(action.get("res_id"))
        self.assertEqual("mail.compose.message", email._name)
