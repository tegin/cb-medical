from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MedicalDocumentType(models.Model):
    # FHIR Entity: Document Refernece
    # (https://www.hl7.org/fhir/documentreference.html)
    _name = 'medical.document.type'
    _description = 'Medical Document Template'
    _inherit = ['medical.abstract', 'mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Name',
        help='Name',
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('current', 'Current'),
        ('superseded', 'Superseded')
    ], required=True, track_visibility=True, default='draft')
    text = fields.Html(sanitize=True)
    template_ids = fields.One2many(
        'medical.document.template',
        inverse_name='document_type_id',
        readonly=True
    )
    current_template_id = fields.Many2one(
        'medical.document.template',
        compute='_compute_current_template'
    )
    current_sequence = fields.Integer(required=True, default=0)
    activity_definition_ids = fields.One2many(
        'workflow.activity.definition',
        inverse_name='document_type_id'
    )
    report_action_id = fields.Many2one(
        'ir.actions.report',
        required=True,
        domain=[('model', '=', 'medical.document.reference')]
    )

    @api.depends('current_sequence')
    def _compute_current_template(self):
        for record in self:
            record.current_template_id = record.template_ids.filtered(
                lambda r: (
                    r.sequence == record.current_sequence and
                    r.state == 'current'
                )
            )

    def _get_internal_identifier(self, vals):
        return self.env['ir.sequence'].next_by_code(
            'medical.document.template') or '/'

    def get_document_template_vals(self):
        return {
            'document_type_id': self.id,
            'state': 'current',
            'text': self.text,
            'sequence': self.current_sequence,
        }

    def post(self):
        self.unpost()
        self.current_sequence += 1
        template = self.env['medical.document.template'].create(
            self.get_document_template_vals()
        )
        self.message_post(
            body='Added template with sequence %s' % template.sequence)

    def unpost(self):
        if self.current_template_id:
            self.current_template_id.unpost()

    @api.multi
    def draft2current(self):
        for record in self:
            record.post()
            record.write({'state': 'current'})

    @api.multi
    def current2superseded(self):
        for record in self:
            if record.activity_definition_ids.filtered(
                    lambda r: r.state == 'active'
            ):
                raise ValidationError(_(
                    'Cannot supersed if it is used on active definitions'
                ))
            record.unpost()
            record.write({'state': 'superseded'})
