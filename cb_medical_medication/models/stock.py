from odoo import fields, models


class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    encounter_id = fields.Many2one(
        'medical.encounter',
        readonly=True,
    )


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    encounter_id = fields.Many2one(
        'medical.encounter',
        readonly=True,
    )
