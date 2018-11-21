# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    invoice_status = fields.Selection(selection_add=[
        ('to preinvoice', 'To Prenvoice'),
        ('preinvoiced', 'Prenvoiced')
    ])

    @api.depends('state', 'order_line.invoice_status',
                 'invoice_group_method_id', 'order_line.preinvoice_group_id')
    def _get_invoiced(self):
        super()._get_invoiced()
        preinvoicing = self.env.ref(
            'cb_medical_sale_invoice_group_method.by_preinvoicing')
        preinvoicing |= self.env.ref(
            'cb_medical_sale_invoice_group_method.no_invoice_preinvoice')
        for order in self:
            if (
                order.state not in ['draft', 'cancel'] and
                order.invoice_group_method_id in preinvoicing
            ):
                if all(line.preinvoice_group_id for line in order.order_line):
                    order.invoice_status = 'preinvoiced'
                else:
                    order.invoice_status = 'to preinvoice'
