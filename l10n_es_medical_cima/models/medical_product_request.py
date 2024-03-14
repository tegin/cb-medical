# Copyright 2022 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalProductRequest(models.Model):

    _inherit = "medical.product.request"

    dispensation_order_number = fields.Integer(default=1)

    expected_dispensation_date = fields.Date()

    diagnostic = fields.Text()

    pharmacist_information = fields.Text()
    patient_information = fields.Text()
    in_patient = fields.Boolean(related="request_order_id.in_patient")

    def _complete_change_state(self):
        res = super()._complete_change_state()
        date = self.expected_dispensation_date
        if not date:
            if self.request_order_id.expected_dispensation_date:
                date = self.request_order_id.expected_dispensation_date
            else:
                date = fields.Date.today()
        res["expected_dispensation_date"] = date
        return res

    def _filter_product(self, product):
        return super()._filter_product(product) and product.in_patient in [
            self.in_patient,
            False,
        ]
