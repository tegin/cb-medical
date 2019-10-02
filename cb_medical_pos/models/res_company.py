from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    patient_journal_id = fields.Many2one(
        "account.journal",
        string="Journal for patient invoices",
        domain="[('company_id', '=', id), ('type', '=', 'sale')]",
    )
