# Copyright 2018 Creu Blanca
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import base64
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class MedicalDocumentReference(models.Model):
    # FHIR Entity: Document Reference
    # (https://www.hl7.org/fhir/documentreference.html)
    _name = 'medical.document.reference'
    _description = 'Medical Document Reference'
    _inherit = 'medical.request'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('current', 'Current'),
        ('superseded', 'Superseded')

    ], required=True, track_visibility=True, default='draft')
    document_type_id = fields.Many2one(
        'medical.document.type',
        required=True,
        ondelete='restrict',
    )
    document_type = fields.Selection(
        related='document_type_id.document_type'
    )
    document_template_id = fields.Many2one(
        'medical.document.template',
        readonly=True,
        ondelete='restrict',
    )
    is_editable = fields.Boolean(
        compute='_compute_is_editable',
    )
    text = fields.Text(
        string='Document text',
        readonly=True,
        sanitize=True
    )

    def check_is_billable(self):
        return self.is_billable

    def _get_internal_identifier(self, vals):
        return self.env['ir.sequence'].next_by_code(
            'medical.document.reference') or '/'

    @api.multi
    @api.depends('state')
    def _compute_is_editable(self):
        for rec in self:
            rec.is_editable = bool(rec.state == 'draft')

    def action_view_request_parameters(self):
        return {
            'view': 'medical_document.medical_document_reference_action',
            'view_form': 'medical.document.reference.view.form', }

    def _get_parent_field_name(self):
        return 'document_reference_id'

    @api.multi
    def print(self):
        return self._print(self.print_action)

    @api.multi
    def render(self):
        return self._print(self.render_report)

    def _print(self, action):
        self.ensure_one()
        if self.state == 'draft':
            return self._draft2current(action)
        return action()

    def render_report(self):
        if self.document_type == 'action':
            return base64.b64encode(
                self.document_type_id.report_action_id.render(self.id)[0])
        raise UserError(_('Function must be defined'))

    def print_action(self):
        if self.document_type == 'action':
            return self.document_type_id.report_action_id.report_action(self)
        raise UserError(_('Function must be defined'))

    @api.multi
    def draft2current(self):
        return self._draft2current(self.print_action)

    @api.multi
    def cancel(self):
        pass

    def _draft2current(self, action):
        self.ensure_one()
        if self.state != 'draft':
            raise ValidationError(_('State must be draft'))
        self.document_template_id = self.document_type_id.current_template_id
        self.text = self.render_text()
        self.write({'state': 'current'})
        return action()

    def render_text(self):
        if self.document_type == 'action':
            return self.document_template_id.render_template(
                self._name, self.id
                )
        raise UserError(_('Function must be defined'))

    @api.multi
    def current2superseded(self):
        if self.filtered(lambda r: r.state != 'current'):
            raise ValidationError(_('State must be Current'))
        self.write({'state': 'superseded'})
