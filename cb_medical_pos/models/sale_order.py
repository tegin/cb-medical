# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    pos_session_id = fields.Many2one(
        comodel_name='pos.session',
        string='PoS Session',
        readonly=1,
    )
    is_down_payment = fields.Boolean(
        default=False
    )
    account_id = fields.Many2one(
        comodel_name='account.account',
        readonly=True
    )
    bank_statement_line_ids = fields.One2many(
        'account.bank.statement.line',
        inverse_name='sale_order_id',
        readonly=True,
    )
    residual = fields.Monetary(
        currency_field='currency_id',
        compute='_compute_residual',
    )

    @api.depends('amount_total', 'bank_statement_line_ids')
    def _compute_residual(self):
        for record in self:
            record.residual = record.amount_total - sum(
                record.statement_line_ids.mapped('amount')
            )

    def create_third_party_move(self):
        res = super().create_third_party_move()
        self.account_id = self.partner_id.with_context(
            force_company=self.company_id.id
        ).property_third_party_customer_account_id
        return res
