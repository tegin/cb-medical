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
