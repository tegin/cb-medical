# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _


class PosSession(models.Model):
    _inherit = 'pos.session'

    validation_status = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In progress'),
        ('finished', 'Finished')
    ], default='draft', required=True, )
    invoice_ids = fields.One2many(
        'account.invoice',
        compute='_compute_invoices',
    )
    sale_order_line_ids = fields.One2many(
        'sale.order.line',
        inverse_name='pos_session_id',
        readonly=1,
    )
    down_payment_ids = fields.One2many(
        'sale.order',
        compute='_compute_down_payments',
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

    @api.depends('sale_order_ids.coverage_agreement_id')
    def _compute_invoices(self):
        for record in self:
            record.invoice_ids = record.sale_order_ids.filtered(
                lambda r: not r.coverage_agreement_id
            ).mapped('invoice_ids')

    @api.depends('sale_order_ids.is_down_payment')
    def _compute_down_payments(self):
        for record in self:
            record.down_payment_ids = record.sale_order_ids.filtered(
                lambda r: r.is_down_payment)

    @api.depends(
        'sale_order_line_ids.request_group_id',
        'sale_order_line_ids.procedure_request_id'
    )
    def _compute_lines(self):
        for record in self:
            record.request_group_ids = record.sale_order_line_ids.mapped(
                'request_group_id')
            record.procedure_request_ids = record.sale_order_line_ids.mapped(
                'procedure_request_id')
            record.procedure_ids = \
                record.sale_order_line_ids.compute_procedure()

    @api.multi
    def action_pos_session_close(self):
        res = super(PosSession, self).action_pos_session_close()

        self.write({'validation_status': 'in_progress'})
        if not self.encounter_ids:
            self.action_validation_finish()
        return res

    @api.multi
    def action_validation_finish(self):
        self.ensure_one()
        self.write({'validation_status': 'finished'})

    @api.multi
    def open_validation_encounter(self, barcode):
        self.ensure_one()
        encounter = self.env['medical.encounter'].search([
            ('internal_identifier', '=', barcode),
            ('pos_session_id', '=', self.id)
        ])
        if not encounter:
            action = self.env.ref(
                'barcode_action.barcode_action_action')
            result = action.read()[0]
            result['context'] = {
                'default_model': 'pos.session',
                'default_method': 'open_validation_encounter',
                'default_session_id': self.id,
                'default_status': _('Encounter %s cannot be found') % barcode,
                'default_status_state': 1,
            }
            return result
        action = self.env.ref(
            'medical_administration_encounter.medical_encounter_action')
        result = action.read()[0]
        res = self.env.ref('medical_encounter.medical_encounter_form', False)
        result['views'] = [(res and res.id or False, 'form')]
        result['res_id'] = encounter.id
        return result
