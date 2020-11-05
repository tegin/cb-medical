from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    change_partner_journal_id = fields.Many2one(
        "account.journal", domain="[('company_id', '=', id)]"
    )
