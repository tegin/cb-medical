from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    def_third_party_product = fields.Many2one(
        "product.product",
        "Third party Product",
        config_parameter="cb.default_third_party_product",
        domain="[('type', '=', 'service')]",
        help="Default product used for third party sale orders",
    )
