from odoo import fields, models


class MedicalCareplanMedication(models.TransientModel):
    _name = "medical.encounter.medication"
    _description = "medical.encounter.medication"

    medical_id = fields.Many2one(
        "medical.encounter", required=True, readonly=True
    )
    product_id = fields.Many2one(
        "product.product",
        required=True,
        domain=[("type", "in", ["consu", "product"])],
    )
    location_id = fields.Many2one(
        "res.partner",
        domain=[
            ("stock_location_id", "!=", False),
            ("is_location", "=", True),
        ],
        required=True,
    )

    def run(self):
        return self.medical_id.add_medication(
            self.location_id, self.product_id
        )
