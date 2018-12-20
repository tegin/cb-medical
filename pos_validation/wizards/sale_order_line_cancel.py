# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrderLineCancel(models.TransientModel):
    _name = 'sale.order.line.cancel'

    sale_order_line_id = fields.Many2one(
        'sale.order.line',
        required=False,
    )
    cancel_reason_id = fields.Many2one(
        'medical.cancel.reason',
        required=True,
    )

    @api.multi
    def run(self):
        return self.sale_order_line_id.medical_cancel(self.cancel_reason_id)
