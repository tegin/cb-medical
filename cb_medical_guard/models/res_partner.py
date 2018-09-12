from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    guard_journal_id = fields.Many2one(
        'account.journal',
        domain=[('type', '=', 'purchase')]
    )
