from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    integer_center_identifier = fields.Integer()
