# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class InvoiceSalesByGroup(models.TransientModel):
    _name = "invoice.sales.by.group"

    @api.model
    def _get_default_merge_draft_invoice(self):
        if self.env.user.company_id.sale_merge_draft_invoice:
            return True
        else:
            return False

    date_to = fields.Date(
        'Up to',
        required=True,
        default=fields.Date.today(),
    )
    invoice_group_method_id = fields.Many2one(
        string='Invoice Group Method',
        comodel_name='sale.invoice.group.method',
        required=True,
    )
    customer_ids = fields.Many2many(
        comodel_name='res.partner',
    )
    company_ids = fields.Many2many(
        comodel_name='res.company',
        string='Companies',
    )
    merge_draft_invoice = fields.Boolean(
        string='Merge with draft invoices',
        default=_get_default_merge_draft_invoice,
        help='Activate this option in order to merge the resulting '
             'invoice with existing draft invoices or deactivate it if you '
             'wish a separate invoice for this sale order.'
    )

    @api.multi
    def invoice_sales_by_group(self):
        sales = self.env['sale.order']
        domain = [
            ('invoice_status', '=', 'to invoice'),
            ('confirmation_date', '<', self.date_to),
            ('invoice_group_method_id', '=', self.invoice_group_method_id.id)]
        if self.customer_ids:
            domain.append(('partner_id', 'in', self.customer_ids.ids))
        if self.company_ids:
            domain.append(('company_id', 'in', self.company_ids.ids))
        sales += sales.search(domain)
        invoices = self.env['account.invoice']
        for sale in sales:
            sale_context = {
                'active_id': sale.id,
                'active_ids': sale.ids,
                'active_model': 'sale.order',
                'open_invoices': True,
            }
            payment = self.env['sale.advance.payment.inv'].with_context(
                force_company=sale.company_id.id,
                company_id=sale.company_id.id,
            ).create(
                {'advance_payment_method': 'delivered',
                 'merge_draft_invoice': self.merge_draft_invoice
                 })
            payment.with_context(sale_context).create_invoices()
            invoices += sale.mapped('invoice_ids')

        # view
        action = self.env.ref('account.action_invoice_tree1')
        result = action.read()[0]
        if not invoices:
            result = action.read()[0]
        if len(invoices) > 1:
            result['domain'] = "[('id', 'in', " + str(invoices.ids) + ")]"
        elif len(invoices) == 1:
            res = self.env.ref('account.invoice.form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = invoices.id
        return result
