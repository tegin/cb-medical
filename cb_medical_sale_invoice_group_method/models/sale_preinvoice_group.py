# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class SalePreinvoiceGroup(models.Model):
    _name = 'sale.preinvoice.group'
    _description = 'Sale Preinvoice Group'
    _inherit = ['medical.abstract']
    _rec_name = 'internal_identifier'

    agreement_id = fields.Many2one(
        comodel_name='medical.coverage.agreement',
        string='Agreement',
        required=True,
        readonly=True
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
        required=True,
        readonly=True
    )
    partner_invoice_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
        required=True,
        readonly=True
    )
    line_ids = fields.One2many(
        string='Validated lines',
        comodel_name='sale.order.line',
        inverse_name='preinvoice_group_id',
    )
    validated_line_ids = fields.One2many(
        string='Validated lines',
        comodel_name='sale.order.line',
        compute='_compute_lines'
    )
    non_validated_line_ids = fields.One2many(
        string='Non validated lines',
        comodel_name='sale.order.line',
        compute='_compute_lines'
    )
    state = fields.Selection(
        string="Status",
        required="True",
        selection=[
            ("draft", "Draft"),
            ("in_progress", "In progress"),
            ("validation", "Pending validation"),
            ("closed", "Closed"),
            ("cancelled", "Cancelled")],
        default="draft",
        help="Current state of the pre-invoice group.",
    )
    current_sequence = fields.Integer(default=1)

    @api.model
    def _get_internal_identifier(self, vals):
        return self.env['ir.sequence'].next_by_code(
            'medical.preinvoice.group') or '/'

    @api.depends('line_ids')
    def _compute_lines(self):
        for record in self:
            record.validated_line_ids = record.line_ids.filtered(
                lambda r: r.is_validated
            )
            record.non_validated_line_ids = record.line_ids.filtered(
                lambda r: not r.is_validated
            )

    def validate_line(self, line):
        if not line.is_validated:
            line.write({
                'is_validated': True,
                'sequence': self.get_sequence()
            })

    def get_sequence(self):
        val = self.current_sequence + 1
        self.write({'current_sequence': val})
        return val

    @api.multi
    @api.depends('internal_identifier')
    def name_get(self):
        result = []
        for record in self:
            name = '[%s]' % record.internal_identifier
            result.append((record.id, name))
        return result

    @api.multi
    def close(self):
        self.ensure_one()
        for line in self.non_validated_line_ids:
            line.preinvoice_group_id = False
        self.write({'state': 'closed'})

    @api.multi
    def start(self):
        self.ensure_one()
        self.write({'state': 'in_progress'})

    @api.multi
    def close_sorting(self):
        self.ensure_one()
        self.write({'state': 'validation'})

    @api.multi
    def cancel(self):
        self.ensure_one()
        for line in self.line_ids:
            line.preinvoice_group_id = False
        self.write({'state': 'cancel'})
