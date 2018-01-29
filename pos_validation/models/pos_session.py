# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models, fields


class PosSession(models.Model):
    _inherit = 'pos.session'

    validation_status = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In progress'),
        ('finished', 'Finished')
    ], default='draft', required=True, )
    invoice_ids = fields.One2many(
        'account.invoice',
        compute='_compute_lines',
    )
    sale_order_line_ids = fields.One2many(
        'sale.order.line',
        compute='_compute_lines',
    )
    down_payment_ids = fields.One2many(
        'sale.order',
        compute='_compute_lines',
    )
    request_group_ids = fields.One2many(
        'medical.request.group',
        compute='_compute_lines',
    )
    procedure_request_ids = fields.One2many(
        'medical.procedure.request',
        compute='_compute_lines',
    )
    procedure_ids = fields.Many2many(
        'medical.procedure',
        compute='_compute_lines',
    )

    @api.depends('sale_order_ids')
    def _compute_lines(self):
        for record in self:
            record.invoice_ids = record.sale_order_ids.filtered(
                lambda r: not r.coverage_agreement_id
            ).mapped('invoice_ids')
            record.down_payment_ids = record.sale_order_ids.filtered(
                lambda r: r.is_down_payment)
            lines = record.sale_order_ids.filtered(
                lambda r: not r.is_down_payment).mapped('order_line')
            record.sale_order_line_ids = lines
            record.request_group_ids = lines.mapped('request_group_id')
            record.procedure_request_ids = lines.mapped('procedure_request_id')
            record.procedure_ids = lines.compute_procedure()

    @api.multi
    def action_pos_session_close(self):
        res = super(PosSession, self).action_pos_session_close()
        self.write({'validation_status': 'in_progress'})
        return res
