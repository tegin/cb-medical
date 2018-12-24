# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    agreement_id = fields.Many2one(
        comodel_name='medical.coverage.agreement',
        string='Agreement',
        readonly=True,
    )
    coverage_template_id = fields.Many2one(
        'medical.coverage.template',
        readonly=True
    )
    invoice_group_method_id = fields.Many2one(
        'invoice.group.method',
        readonly=True,
    )

    @api.model
    def _prepare_refund(
            self, invoice, date_invoice=None, date=None, description=None,
            journal_id=None):
        vals = super(AccountInvoice, self)._prepare_refund(
            invoice, date_invoice=date_invoice, date=date,
            description=description, journal_id=journal_id)
        vals['agreement_id'] = invoice.agreement_id.id
        vals['coverage_template_id'] = invoice.coverage_template_id.id
        vals['invoice_group_method_id'] = invoice.invoice_group_method_id.id
        return vals
