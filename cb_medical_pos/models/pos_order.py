# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PosOrder(models.Model):
    _inherit = "pos.order"

    sale_order_id = fields.Many2one("sale.order")
    encounter_id = fields.Many2one("medical.encounter")
    is_deposit = fields.Boolean()
    deposit_line_id = fields.Many2one("account.move.line")
