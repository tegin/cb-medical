# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    preinvoice_status = fields.Selection([
        ('draft', 'Draft'),
        ('to preinvoice', 'To Prenvoice'),
        ('preinvoiced', 'Prenvoiced')
    ], store=True, compute='_compute_preinvoice_status')

    @api.depends('state', 'order_line.invoice_status',
                 'order_line.invoice_group_method_id',
                 'order_line.preinvoice_group_id')
    def _compute_preinvoice_status(self):
        preinvoicing = self.env.ref(
            'cb_medical_careplan_sale.by_preinvoicing')
        preinvoicing |= self.env.ref(
            'cb_medical_careplan_sale.no_invoice_preinvoice')
        for order in self:
            if (
                order.state not in ['draft', 'cancel']
            ):
                if all(
                    line.preinvoice_group_id for line in
                    order.order_line.filtered(
                        lambda r: r.invoice_group_method_id in preinvoicing)
                ):
                    order.preinvoice_status = 'preinvoiced'
                else:
                    order.preinvoice_status = 'to preinvoice'
            else:
                order.preinvoice_status = 'draft'

    @api.model
    def _get_invoice_group_key(self, order):
        if order.coverage_agreement_id:
            return (
                order.partner_invoice_id.id,
                order.currency_id.id,
                order.company_id.id,
                order.coverage_agreement_id.id
            )
        return super()._get_invoice_group_key(order)

    @api.model
    def _get_invoice_group_line_key(self, line):
        if line.invoice_group_method_id and not self.env.context.get(
            'no_split_invoices', False
        ):
            return (
                line.order_id.partner_invoice_id.id,
                line.order_id.currency_id.id,
                line.order_id.company_id.id,
                line.order_id.coverage_agreement_id.id,
                line.invoice_group_method_id.id,
            )
        return super()._get_invoice_group_line_key(line)

    @api.model
    def _get_draft_invoices(self, invoices, references):
        invs, refs = super()._get_draft_invoices(invoices, references)
        method = self.env.context.get('invoice_group_method_id', False)
        if method and self.env.context.get('merge_draft_invoice', False):
            domain = [
                ('state', '=', 'draft'),
            ]
            companies = self.env.context.get('companies')
            if companies:
                domain.append(('company_id', 'in', companies))
            customers = self.env.context.get('customers')
            if customers:
                domain.append(('partner_id', 'in', customers))
            draft_inv = self.env['account.invoice'].search(domain)
            for inv in draft_inv:
                for line in inv.invoice_line_ids.mapped('sale_line_ids'):
                    ref_order = self._get_invoice_group_line_key(line)
                    group_inv_key = self._get_invoice_group_key(ref_order)
                    refs[inv] = ref_order
                    invs[group_inv_key] = inv
        return invs, refs
