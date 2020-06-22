from odoo import fields, models

from odoo.addons import decimal_precision as dp


class MedicalRequest(models.AbstractModel):
    _inherit = "medical.request"

    medical_sale_discount_id = fields.Many2one(
        "medical.sale.discount", readonly=True
    )
    discount = fields.Float(readonly=True, digits=dp.get_precision("Discount"))

    def get_sale_order_line_vals(self, is_insurance):
        vals = super().get_sale_order_line_vals(is_insurance)
        if self.medical_sale_discount_id:
            vals["discount"] = self.discount or 0.0
            vals["medical_sale_discount_id"] = self.medical_sale_discount_id.id
        return vals
