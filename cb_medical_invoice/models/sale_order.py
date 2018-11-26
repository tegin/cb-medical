from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    encounter_final_sale_order = fields.Boolean(readonly=True)
