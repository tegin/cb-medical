# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class WizardSalePreinvoiceGroup(models.TransientModel):
    _name = "wizard.sale.preinvoice.group"

    company_ids = fields.Many2many(
        comodel_name='res.company',
        string='Companies',
    )
    partner_ids = fields.Many2many(
        comodel_name='res.partner',
        domain=[('is_payor', '=', True)],
        string='Payors',
    )

    def run(self):
        domain = [
            ('invoice_status', '=', 'to invoice'),
            ('invoice_group_method_id', '=', self.env.ref(
                'cb_medical_sale_invoice_group_method.by_preinvoicing').id),
        ]
        if self.company_ids:
            domain.append(('company_id', 'in', self.company_ids.ids))
        if self.partner_ids:
            domain.append(('partner_id', 'in', self.partner_ids.ids))
        sale_orders = self.env['sale.order'].search(domain)
        agreements = {}
        for sale_order in sale_orders:
            for line in sale_order.order_line.filtered(
                    lambda r: not r.preinvoice_group_id
            ):
                cov_id = sale_order.coverage_agreement_id.id
                partner_invoice_id = sale_order.partner_invoice_id.id
                partner_id = sale_order.partner_id.id
                if cov_id not in agreements:
                    agreements[cov_id] = {}
                if partner_id not in agreements[cov_id]:
                    agreements[cov_id][partner_id] = {}
                if partner_invoice_id not in agreements[cov_id][partner_id]:
                    agreements[cov_id][partner_id][
                        partner_invoice_id
                    ] = self.env['sale.preinvoice.group'].create({
                        'agreement_id': cov_id,
                        'company_id': sale_order.company_id.id,
                        'partner_id': partner_id,
                        'partner_invoice_id': partner_invoice_id,
                        'current_sequence': 0,
                    })
                line.sequence = 999999
                line.is_validated = False
                line.preinvoice_group_id = agreements[cov_id][partner_id][
                    partner_invoice_id]
        action = self.env.ref(
            'cb_medical_sale_invoice_group_method.sale_preinvoice_group_action'
        )
        result = action.read()[0]
        return result
