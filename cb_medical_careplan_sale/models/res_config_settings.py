from ast import literal_eval

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    default_third_party_product = fields.Many2one(
        "product.product",
        "Third party Product",
        domain="[('type', '=', 'service')]",
        help="Default product used for third party sale orders",
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        default_third_party_product = literal_eval(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("cb.default_third_party_product", default="False")
        )
        if (
            default_third_party_product
            and not self.env["product.product"]
            .browse(default_third_party_product)
            .exists()
        ):
            default_third_party_product = False
        res.update(default_third_party_product=default_third_party_product)
        return res

    @api.multi
    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env["ir.config_parameter"].sudo().set_param(
            "cb.default_third_party_product",
            self.default_third_party_product.id,
        )
        return res
