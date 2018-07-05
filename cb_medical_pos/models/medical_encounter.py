# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class MedicalEncounter(models.Model):
    _inherit = 'medical.encounter'

    pos_session_id = fields.Many2one(
        comodel_name='pos.session',
        string='PoS Session',
        readonly=1,
        track_visibility=True,
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        readonly=1,
        track_visibility=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='company_id.currency_id', readonly=True,
    )
    pending_private_amount = fields.Monetary(
        currency_field='currency_id',
        compute='_compute_pending_private_amount'
    )

    @api.depends(
        'sale_order_ids.coverage_agreement_id',
        'sale_order_ids.amount_total',
        'sale_order_ids.invoice_ids.amount_total',
        'sale_order_ids.invoice_ids.bank_statement_line_ids')
    def _compute_pending_private_amount(self):
        for record in self:
            inv = record.sale_order_ids.filtered(
                lambda r: not r.coverage_agreement_id and r.invoice_ids
            ).mapped('invoice_ids')
            orders = record.sale_order_ids.filtered(
                lambda r: not r.coverage_agreement_id and not r.invoice_ids
            )
            record.pending_private_amount = (
                sum(inv.mapped('amount_total')) -
                sum(inv.mapped('bank_statement_line_ids').mapped('amount')) +
                sum(orders.mapped('amount_total')) -
                sum(orders.mapped('bank_statement_line_ids').mapped('amount'))
            )

    def _get_sale_order_vals(
            self, partner, cov, agreement, third_party_partner, is_insurance
    ):
        vals = super()._get_sale_order_vals(
            partner, cov, agreement, third_party_partner, is_insurance)
        session = self.pos_session_id.id or self._context.get('pos_session_id')
        if session:
            vals['pos_session_id'] = session
        if not is_insurance:
            if not self.company_id.id and not self._context.get('company_id'):
                raise ValidationError(_(
                    'Company is required in order to create Sale Orders'))
            vals['company_id'] = (
                self.company_id.id or
                self._context.get('company_id'))
        return vals

    def inprogress2onleave_values(self):
        res = super().inprogress2onleave_values()
        if not self.company_id:
            if not self._context.get('company_id', False):
                raise ValidationError(_('Company is required'))
            res['company_id'] = self._context.get('company_id', False)
        if self._context.get('pos_session_id', False):
            res['pos_session_id'] = self._context.get('pos_session_id', False)
        return res

    @api.multi
    def inprogress2onleave(self):
        self.create_sale_order()
        res = super().inprogress2onleave()
        if not self.sale_order_ids.filtered(
                lambda r: not r.coverage_agreement_id and not r.is_down_payment
        ):
            self.onleave2finished()
        return res

    def finish_sale_order(self, sale_order):
        if not self._context.get('journal_id', False):
            raise ValidationError(_(
                'Payment journal is necessary in order to finish sale orders'))
        if not self._context.get('pos_session_id', False):
            raise ValidationError(_(
                'Payment journal is necessary in order to finish sale orders'))
        sale_order.action_confirm()
        journal_id = self._context.get('journal_id', False)
        pos_session_id = self._context.get('pos_session_id', False)
        cash_vals = {
            'journal_id': journal_id,
        }
        if not sale_order.third_party_order:
            model = 'cash.invoice.out'
            patient_journal = sale_order.company_id.patient_journal_id.id
            invoice = self.env['account.invoice'].browse(
                sale_order.with_context(
                    default_journal_id=patient_journal
                ).action_invoice_create())
            invoice.action_invoice_open()
            cash_vals.update({
                'invoice_id': invoice.id,
                'amount': invoice.amount_total,
            })
        else:
            model = 'cash.sale.order.out'
            cash_vals.update({
                'sale_order_id': sale_order.id,
                'amount': sale_order.amount_total,
            })
        process = self.env[model].with_context(
            active_ids=[pos_session_id], active_model='pos.session'
        ).create(cash_vals)
        process.run()

    def onleave2finished_values(self):
        res = super().onleave2finished_values()
        if self._context.get('pos_session_id', False):
            res['pos_session_id'] = self._context.get('pos_session_id', False)
        return res

    @api.multi
    def onleave2finished(self):
        sale_orders = self.sale_order_ids.filtered(
            lambda r: not r.coverage_agreement_id and not r.is_down_payment)
        for sale_order in sale_orders:
            self.finish_sale_order(sale_order)
        return super().onleave2finished()

    def down_payment_inverse_vals(self, order, line):
        return {
            'order_id': order.id,
            'product_id': line.product_id.id,
            'name': line.name,
            'product_uom_qty': line.product_uom_qty,
            'product_uom': line.product_uom.id,
            'price_unit': - line.price_unit,
        }

    def get_sale_order_lines(self):
        values = super().get_sale_order_lines()
        down_payments = self.sale_order_ids.filtered(
            lambda r: r.is_down_payment and r.coverage_agreement_id is False
        )
        if down_payments:
            if 0 not in values:
                values[0] = {}
            if self.get_patient_partner() not in values[0]:
                values[0][self.get_patient_partner()] = {}
            if 0 not in values[0][self.get_patient_partner()]:
                values[0][self.get_patient_partner()][0] = []
        return values

    def _generate_sale_order(
            self, key, cov, partner, third_party_partner, order_lines
    ):
        order = super()._generate_sale_order(
            key, cov, partner, third_party_partner, order_lines
        )
        if key == 0:
            orders = self.sale_order_ids.filtered(
                lambda r: (
                    r.is_down_payment and r.coverage_agreement_id is False
                )
            )
            for pay in orders:
                for line in pay.order_line:
                    self.env['sale.order.line'].create(
                        self.down_payment_inverse_vals(order, line)
                    )
        return order
