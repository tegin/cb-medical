# Copyright 2022 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_round


class MedicalProductRequest(models.Model):

    _inherit = "medical.product.request"

    rate_quantity = fields.Float(compute="_compute_rate_from_specific_rate")

    rate_uom_id = fields.Many2one(compute="_compute_rate_from_specific_rate")

    specific_rate = fields.Float(default=8)

    specific_rate_uom_id = fields.Many2one(
        "uom.uom", default=lambda self: self.env.ref("uom.product_uom_hour").id
    )

    dispensation_order_number = fields.Integer(default=1)

    expected_dispensation_date = fields.Date()

    diagnostic = fields.Text()

    pharmacist_information = fields.Text()
    patient_information = fields.Text()

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

    @api.constrains("specific_rate")
    def _check_specific_rate_quantity(self):
        for rec in self:
            if rec.product_type == "medication" and rec.specific_rate < 1:
                raise ValidationError(_("Rate must be positive"))

    # This computation will have sense once we do the electronic prescription.
    # We will have to think about what happens when we have decimals.
    # For example, every 72 hours, which gives 2'33...
    # Now is it rounded until the most proximal 0.5 up. In this case it would be 2.5.
    @api.depends("specific_rate", "specific_rate_uom_id")
    def _compute_rate_from_specific_rate(self):
        for rec in self:
            if rec.specific_rate_uom_id == self.env.ref(
                "uom.product_uom_hour"
            ):
                if rec.specific_rate <= 24:
                    rate = 24 / rec.specific_rate
                    rate_uom_id = self.env.ref("uom.product_uom_day").id
                else:
                    rate = 24 * 7 / rec.specific_rate
                    rate_uom_id = self.env.ref(
                        "cb_medical_product_request.product_uom_week"
                    ).id
            elif rec.specific_rate_uom_id == self.env.ref(
                "uom.product_uom_day"
            ):
                rate = 7 / rec.specific_rate
                rate_uom_id = self.env.ref(
                    "cb_medical_product_request.product_uom_week"
                ).id
            else:  # specific_rate_uom_id == week
                rate = 1 / rec.specific_rate
                rate_uom_id = self.env.ref(
                    "cb_medical_product_request.product_uom_week"
                ).id
            rate_rounded = 0.5 * float_round(
                rate / 0.5, precision_digits=0, rounding_method="UP"
            )
            rec.rate_quantity = rate_rounded
            rec.rate_uom_id = rate_uom_id
