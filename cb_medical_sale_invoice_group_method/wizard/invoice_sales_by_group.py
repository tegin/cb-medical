# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class InvoiceSalesByGroup(models.TransientModel):
    _name = "invoice.sales.by.group"

    @api.model
    def _get_default_merge_draft_invoice(self):
        return bool(self.env.user.company_id.sale_merge_draft_invoice)

    date_to = fields.Date(
        'Up to',
        required=True,
        default=fields.Date.today(),
    )
    invoice_group_method_id = fields.Many2one(
        string='Invoice Group Method',
        comodel_name='invoice.group.method',
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
        domain = [
            ('invoice_status', '=', 'to invoice'),
            ('confirmation_date', '<', self.date_to),
        ]
        if self.customer_ids:
            domain.append(('partner_id', 'in', self.customer_ids.ids))
        if self.company_ids:
            domain.append(('company_id', 'in', self.company_ids.ids))
        sales = self.env['sale.order'].search(domain)
        invoices = sales.with_context(
            customers=self.customer_ids.ids,
            companies=self.company_ids.ids,
            invoice_group_method_id=self.invoice_group_method_id.id,
            no_check_lines=True,
            merge_draft_invoice=self.merge_draft_invoice
        ).action_invoice_create()
        # view
        action = self.env.ref('account.action_invoice_tree1')
        result = action.read()[0]
        if not invoices:
            result = action.read()[0]
        if len(invoices) > 1:
            result['domain'] = "[('id', 'in', " + str(invoices) + ")]"
        elif len(invoices) == 1:
            res = self.env.ref('account.invoice.form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = invoices[0]
        return result
