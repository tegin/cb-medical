from odoo import api, fields, models


class MedicalEncounter(models.Model):
    _inherit = 'medical.encounter'

    invoice_count = fields.Integer(compute='_compute_invoice_count')

    invoice_line_ids = fields.One2many(comodel_name='account.invoice.line',
                                       inverse_name='encounter_id',
                                       string='Invoice Lines')

    @api.depends('invoice_line_ids')
    def _compute_invoice_count(self):
        for record in self:
            invoices = self.env['account.invoice.line'].search(
                [('encounter_id', '=', record.id)]).mapped('invoice_id')
            record.invoice_count = len(invoices)

    def _get_sale_order_vals(
        self, partner, cov, agreement, third_party_partner, is_insurance
    ):
        vals = super()._get_sale_order_vals(
            partner, cov, agreement, third_party_partner, is_insurance)
        vals['patient_name'] = self.patient_id.display_name
        return vals

    def action_view_invoice(self):
        self.ensure_one()
        action = self.env.ref('account.action_invoice_tree1')
        result = action.read()[0]
        invoices = self.env['account.invoice.line'].search(
            [('encounter_id', '=', self.id)]).mapped('invoice_id')
        result['domain'] = [('id', 'in', invoices.ids)]
        if len(invoices) == 1:
            res = self.env.ref('account.invoice_form')
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = invoices.id
        return result
