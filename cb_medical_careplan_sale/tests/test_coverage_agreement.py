from odoo.addons.medical_financial_coverage_agreement.tests import common
from odoo.exceptions import ValidationError


class TestMedicalCoverageAgreement(common.AgrementSavepointCase):
    @classmethod
    def _create_coverage_agreement_vals(cls, coverage_template):
        result = super()._create_coverage_agreement_vals(coverage_template)
        result.update(
            {
                "authorization_method_id": cls.env.ref(
                    "medical_financial_coverage_request.without"
                ).id,
                "authorization_format_id": cls.env.ref(
                    "medical_financial_coverage_request.format_anything"
                ).id,
            }
        )
        return result

    @classmethod
    def _create_coverage_agreement_item_vals(cls, coverage_agreement, product):
        result = super()._create_coverage_agreement_item_vals(
            coverage_agreement, product
        )
        result.update(
            {
                "authorization_method_id": cls.env.ref(
                    "medical_financial_coverage_request.without"
                ).id,
                "authorization_format_id": cls.env.ref(
                    "medical_financial_coverage_request.format_anything"
                ).id,
            }
        )
        return result

    def test_join_agreements_constrain_01(self):
        agr = self._create_coverage_agreement(self.coverage_template_1)
        agr2 = self._create_coverage_agreement(self.coverage_template_1)
        self._create_coverage_agreement_item(agr, self.product_1)
        self._create_coverage_agreement_item(agr2, self.product_2)
        (agr | agr2).write({"center_ids": [(4, self.center_1.id)]})
        agr.invoice_group_method_id = self.env.ref(
            "cb_medical_careplan_sale.by_customer"
        )
        with self.assertRaises(ValidationError):
            self.env["medical.coverage.agreement.join"].with_context(
                active_model=(agr | agr2)._name, active_ids=(agr | agr2).ids,
            ).create({}).run()

    def test_join_agreements_constrain_02(self):
        agr = self._create_coverage_agreement(self.coverage_template_1)
        agr2 = self._create_coverage_agreement(self.coverage_template_1)
        self._create_coverage_agreement_item(agr, self.product_1)
        self._create_coverage_agreement_item(agr2, self.product_2)
        (agr | agr2).write({"center_ids": [(4, self.center_1.id)]})
        agr.invoice_group_method_id = self.env.ref(
            "cb_medical_careplan_sale.by_customer"
        )
        agr2.invoice_group_method_id = self.env.ref(
            "cb_medical_careplan_sale.by_patient"
        )
        with self.assertRaises(ValidationError):
            self.env["medical.coverage.agreement.join"].with_context(
                active_model=(agr | agr2)._name, active_ids=(agr | agr2).ids,
            ).create({}).run()
