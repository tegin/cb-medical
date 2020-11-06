# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class MedicalMedicationRequest(models.Model):
    _inherit = "medical.medication.request"

    location_type_id = fields.Many2one(
        "medical.location.type", readonly=True, track_visibility="onchange"
    )

    def _get_event_values(self):
        res = super()._get_event_values()
        if self.env.context.get("product_id", False):
            res["product_id"] = self.env.context.get("product_id")
            res["product_uom_id"] = self.env.context.get("product_uom_id")
            res["qty"] = self.env.context.get("qty", 1)
            res["amount"] = self.env.context.get("amount", 0)
        if self.env.context.get("location_id", False):
            res["location_id"] = self.env.context.get("location_id")
        return res

    def _add_medication_item(self, item):
        if self.state == "draft":
            self.draft2active()
        administration = self.with_context(
            product_id=item.product_id.id,
            product_uom_id=item.product_id.uom_id.id,
            qty=item.qty,
            amount=item.price * item.qty,
            location_id=item.location_id.id,
            tracking_disable=True,
        ).generate_event()
        administration.preparation2in_progress()
        if not self.env.context.get("no_complete_administration", False):
            administration.with_context(
                no_post_move=True
            ).in_progress2completed()
        return administration

    def get_sale_order_line_vals(self, is_insurance):
        res = super().get_sale_order_line_vals(is_insurance)
        if self.location_type_id:
            res["name"] = "{} en {}".format(
                res["name"], self.location_type_id.name,
            )
        return res
