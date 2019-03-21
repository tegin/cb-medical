from odoo import fields, models


class WizardSalePreinvoiceGroup(models.TransientModel):
    _inherit = "wizard.sale.preinvoice.group"

    payor_ids = fields.Many2many(
        domain=['|', ('is_payor', '=', True), ('agent', '=', True)],
    )
