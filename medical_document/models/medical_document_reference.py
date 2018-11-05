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
    _inherit = ['medical.request', 'medical.document.language']

    internal_identifier = fields.Char(
        string="Document reference"
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('current', 'Current'),
        ('superseded', 'Superseded')

    ], required=True, track_visibility=True, default='draft')
    document_type_id = fields.Many2one(
        'medical.document.type',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        ondelete='restrict',
    )
    document_type = fields.Selection(
        related='document_type_id.document_type',
        readonly=True,
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
    lang = fields.Selection(
        required=False, readonly=True,
        states={'draft': [('readonly', False)]},
    )

    def _get_language(self):
        return self.lang or self.patient_id.lang

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
    def view(self):
        return self._print(self.view_action)

    @api.multi
    def render(self):
        return self._print(self.render_report)

    def _print(self, action):
        self.ensure_one()
        if self.state == 'draft':
            return self._draft2current(action)
        return action()

    def _render(self):
        return self.with_context(
            lang=self.lang
        ).document_type_id.report_action_id.render(self.id)

    def render_report(self):
        return base64.b64encode(self._render()[0])

    def view_action(self):
        if self.document_type == 'action':
            return self.document_type_id.report_action_id.report_action(self)
        raise UserError(_('Function must be defined'))

    def _get_printer_usage(self):
        return 'standard'

    def print_action(self):
        content, mime = self._render()
        behaviour = self.remote.with_context(
            printer_usage=self._get_printer_usage()
        ).get_printer_behaviour()
        if 'printer' not in behaviour:
            return False
        printer = behaviour.pop('printer')
        return printer.print_document(
            report=self.document_type_id.report_action_id,
            content=content, doc_format=mime
        )

    @api.multi
    def draft2current(self):
        return self._draft2current(self.print_action)

    @api.multi
    def cancel(self):
        pass

    def draft2current_values(self):
        template_id = self.document_type_id.current_template_id.id
        return {
            'lang': self._get_language(),
            'document_template_id': template_id,
            'text': self.with_context(
                template_id=template_id,
                render_language=self._get_language()
            ).render_text()
        }

    @api.multi
    def change_lang(self, lang):
        text = self.with_context(
            template_id=self.document_template_id.id,
            render_language=lang
        ).render_text()
        return self.write({
            'lang': lang,
            'text': text,
        })

    def _draft2current(self, action):
        self.ensure_one()
        if self.state != 'draft':
            raise ValidationError(_('State must be draft'))
        vals = self.draft2current_values()
        res = action()
        if res:
            vals.update({'state': 'current'})
        self.write(vals)
        return res

    def render_text(self):
        if self.document_type == 'action':
            template = (
                self.document_template_id or
                self.env['medical.document.template'].browse(
                    self._context.get('template_id', False))
            )
            return template.render_template(self._name, self.id)
        raise UserError(_('Function must be defined'))

    def current2superseded_values(self):
        return {'state': 'superseded'}

    @api.multi
    def current2superseded(self):
        if self.filtered(lambda r: r.state != 'current'):
            raise ValidationError(_('State must be Current'))
        self.write(self.current2superseded_values())
