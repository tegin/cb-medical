from odoo import models


class MedicalEncounter(models.Model):
    _inherit = 'medical.encounter'

    def _get_sale_order_vals(
        self, partner, cov, agreement, third_party_partner, is_insurance, group
    ):
        vals = super()._get_sale_order_vals(
            partner, cov, agreement, third_party_partner, is_insurance, group)
        vals['patient_name'] = self.patient_id.display_name
        return vals
