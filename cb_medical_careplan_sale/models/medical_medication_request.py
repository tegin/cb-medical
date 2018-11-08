# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class MedicalMedicationRequest(models.Model):
    _inherit = 'medical.medication.request'

    def check_is_billable(self):
        return self.is_billable

    def compute_price(self, is_insurance):
        cai = self.coverage_agreement_item_id
        medication_price = 0.0
        for admin in self.medication_administration_ids:
            medication_price += admin.price
        percentage = cai.coverage_percentage
        if not is_insurance:
            percentage = 1 - percentage
        return (medication_price * percentage)/100

    @api.depends('is_billable', 'sale_order_line_ids',
                 'coverage_agreement_item_id', 'state')
    def _compute_is_sellable(self):
        for rec in self:
            ca = rec.coverage_agreement_id
            rec.is_sellable_private = bool(
                rec.state not in ['cancelled'] and
                rec.is_billable and
                len(rec.sale_order_line_ids.filtered(
                    lambda r: (
                        r.state != 'cancel' and
                        not r.order_id.coverage_agreement_id)
                )) == 0 and
                (rec.coverage_agreement_item_id.coverage_percentage < 100)
            )
            rec.is_sellable_insurance = bool(
                rec.state not in ['cancelled'] and
                rec.is_billable and
                len(rec.sale_order_line_ids.filtered(
                    lambda r: (
                        r.state != 'cancel' and
                        r.order_id.coverage_agreement_id.id == ca.id)
                )) == 0 and
                rec.coverage_agreement_item_id.coverage_percentage > 0
            )
