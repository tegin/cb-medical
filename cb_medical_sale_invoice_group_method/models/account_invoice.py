# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    agreement_id = fields.Many2one(
        comodel_name='medical.coverage.agreement',
        string='Agreement',
        readonly=True,
    )
    invoice_group_method_id = fields.Many2one(
        'invoice.group.method',
        readonly=True,
    )
