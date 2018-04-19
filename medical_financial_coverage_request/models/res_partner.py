from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    encounter_sequence_id = fields.Many2one(
        'ir.sequence',
        'Encounter sequence',
    )
