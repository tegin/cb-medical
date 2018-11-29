from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    location_type_id = fields.Many2one(
        'medical.location.type',
    )
