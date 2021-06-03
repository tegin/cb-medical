# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class MedicalMedicationRequest(models.Model):
    _inherit = "medical.medication.request"

    def check_is_billable(self):
        return self.is_billable

    def compute_price(self, is_insurance):
        cai = (
            self.coverage_agreement_item_id
            or self.request_group_id.coverage_agreement_item_id
        )
        medication_price = 0.0
        for admin in self.medication_administration_ids:
            medication_price += admin.amount
        percentage = cai.coverage_percentage
        if not is_insurance:
            percentage = 100 - percentage
        return (medication_price * percentage) / 100

    def check_sellable(self, is_insurance, agreement_item):
        if is_insurance:
            return agreement_item.coverage_percentage > 0
        return agreement_item.coverage_percentage < 100
