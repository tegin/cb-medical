# Copyright (C) 2017 Creu Blanca
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    sale_order_id = fields.Many2one(
        'sale.order',
        string='Sale Order',
        readonly=True
    )

    @api.multi
    def fast_counterpart_creation(self):
        for st_line in self:
            if not st_line.sale_order_id:
                super(
                    AccountBankStatementLine, st_line
                ).fast_counterpart_creation()
            else:
                sale_order = st_line.sale_order_id
                if not sale_order.third_party_order:
                    raise ValidationError(_(
                        'Sale Order must be a third party order'))
                move_line = sale_order.third_party_move_id.line_ids.filtered(
                    lambda r: r.account_id.id == sale_order.account_id.id
                )
                if move_line.amount != 0:
                    vals = {
                        'name': st_line.name,
                        'debit': st_line.amount < 0 and -st_line.amount or 0.0,
                        'credit': st_line.amount > 0 and st_line.amount or 0.0,
                        'move_line': move_line
                    }
                    st_line.process_reconciliation(
                        counterpart_aml_dicts=[vals])
