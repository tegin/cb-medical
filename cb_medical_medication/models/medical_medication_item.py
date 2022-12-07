from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MedicalMedicationItem(models.Model):
    _name = "medical.medication.item"
    _description = "medical.medication.item"

    encounter_id = fields.Many2one("medical.encounter", readonly=True, required=True)
    product_id = fields.Many2one(
        "product.product",
        required=True,
        domain=[("type", "in", ["consu", "product"])],
    )
    categ_id = fields.Many2one(
        "product.category", related="product_id.categ_id", readonly=True
    )
    location_id = fields.Many2one(
        "res.partner",
        domain=[
            ("stock_location_id", "!=", False),
            ("is_location", "=", True),
        ],
        required=True,
    )
    qty = fields.Integer(required=True, default=1)
    price = fields.Float(required=True)
    is_phantom = fields.Integer(default=False)
    amount = fields.Float(compute="_compute_amount", store=True)

    @api.depends("qty", "price")
    def _compute_amount(self):
        for rec in self:
            rec.amount = rec.qty * rec.price

    @api.onchange("product_id")
    def _onchange_product(self):
        self.price = self.product_id.list_price

    def _to_medication_request(self, data):
        product = self.product_id.categ_id.category_product_id
        if data.get(product.id, {}).get(self.location_id.location_type_id.id, False):
            request = data.get(product.id, {}).get(
                self.location_id.location_type_id.id, False
            )
            request._add_medication_item(self)
            return product.id, self.location_id.location_type_id.id, request
        requests = (
            self.encounter_id.mapped("careplan_ids")
            .mapped("medication_request_ids")
            .filtered(
                lambda r: (
                    r.product_id == product
                    and r.state in ["draft", "active"]
                    and r.location_type_id == self.location_id.location_type_id
                )
            )
        )
        if not requests:
            requests = (
                self.encounter_id.mapped("careplan_ids")
                .mapped("medication_request_ids")
                .filtered(
                    lambda r: (
                        r.product_id == product
                        and not r.location_type_id
                        and r.state in ["draft", "active"]
                    )
                )
            )
        # We are adding the information on the first medication request that
        # is not sellable
        for request in requests.filtered(
            lambda r: not r.request_group_id.child_id
            and not r.request_group_id.child_model
        ):
            request._add_medication_item(self)
            return product.id, self.location_id.location_type_id.id, request
        # That is sellable to insurance
        for request in requests.filtered(
            lambda r: r.request_group_id.is_sellable_insurance
        ):
            request._add_medication_item(self)
            return product.id, self.location_id.location_type_id.id, request
        # That is sellable to patient
        for request in requests.filtered(
            lambda r: r.request_group_id.is_sellable_private
        ):
            request._add_medication_item(self)
            return product.id, self.location_id.location_type_id.id, request
        # If no medications are found, we are returning an error
        raise ValidationError(
            _("Request cannot be found for category %s")
            % self.product_id.categ_id.display_name
        )
