from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    third_party_sale_journal_id = fields.Many2one(
        'account.journal',
        domain="[('company_id', '=', active_id), ('type', '=', 'sale')]"
    )
