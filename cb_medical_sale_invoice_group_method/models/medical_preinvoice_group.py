# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MedicalPreinvoiceGroup(models.Model):
    _name = 'medical.preinvoice.group'
    _description = 'Medical Preinvoice Group'
    _inherit = ['barcodes.barcode_events_mixin', 'medical.abstract']
    _rec_name = 'name'

    name = fields.Char(
        string='Pre-invoice Group name',
        default='/',
    )
    validated_line_ids = fields.One2many(
        string='Validated lines',
        comodel_name='sale.order.line',
        inverse_name='preinvoice_group_id',
    )
    non_validated_line_ids = fields.One2many(
        string='Non validated lines',
        comodel_name='sale.order.line',
        compute='_compute_non_validated_line_ids',
    )
    status = fields.Selection(
        string="Status",
        required="True",
        selection=[
            ("draft", "Draft"),
            ("in_progress", "In progress"),
            ("closed", "Closed"),
            ("cancelled", "Cancelled")],
        default="draft",
        help="Current state of the pre-invoice group.",
    )
    encounter_id = fields.Many2one(
        comodel_name='medical.encounter',
        string='Medical Encounter',
    )

    @api.model
    def _get_internal_identifier(self, vals):
        return self.env['ir.sequence'].next_by_code(
            'medical.preinvoice.group') or '/'

    def on_barcode_scanned(self, barcode):
        encounter = self.env['medical.encounter'].search([(
            'internal_identifier', '=', barcode)], limit=1)
        if encounter:
            self.encounter_id = encounter

    def validate_lines(self):
        lines = self.env['sale.order.line'].search([
            ('id', 'in', self.non_validated_line_ids.ids),
            ('encounter_id', '=', self.encounter_id.id)])
        for line in lines:
            line.validate_line(self)

    @api.multi
    @api.depends('name', 'internal_identifier')
    def name_get(self):
        result = []
        for record in self:
            name = '[%s]' % record.internal_identifier
            if record.name:
                name = '%s %s' % (name, record.name)
            result.append((record.id, name))
        return result

    @api.multi
    def _compute_non_validated_line_ids(self):
        sales = self.env['sale.order'].search([
            ('invoice_status', '=', 'to invoice'),
            ('invoice_group_method_id', '=', self.env.ref(
                'medical_sale_invoice_group_method.by_preinvoicing').id),
        ])
        for rec in self:
            for sale in sales:
                for sale_line in sale.order_line:
                    if not sale_line.is_validated:
                        rec.non_validated_line_ids += sale_line
