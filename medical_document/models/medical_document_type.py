from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MedicalDocumentType(models.Model):
    # FHIR Entity: Document Refernece
    # (https://www.hl7.org/fhir/documentreference.html)
    _name = 'medical.document.type'
    _description = 'Medical Document Type'
    _inherit = ['medical.abstract', 'mail.thread', 'mail.activity.mixin']

    document_type = fields.Selection([
        ('action', 'Report action')
    ], required=True, default='action')

    name = fields.Char(
        string='Name',
        help='Name',
        translate=True,
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('current', 'Current'),
        ('superseded', 'Superseded')
    ], required=True, track_visibility=True, default='draft')
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
        domain=[('model', '=', 'medical.document.reference')]
    )
    lang_ids = fields.One2many(
        'medical.document.type.lang',
        inverse_name='document_type_id'
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
            'lang_ids': [
                (0, 0, lang.get_document_template_lang_vals())
                for lang in self.lang_ids
            ],
            'sequence': self.current_sequence,
        }

    @api.multi
    def post(self):
        self.ensure_one()
        self.unpost()
        self.current_sequence += 1
        template = self.env['medical.document.template'].create(
            self.get_document_template_vals()
        )
        self.message_post(
            body=_('Added template with sequence %s') % template.sequence)
        return True

    def unpost(self):
        if self.current_template_id:
            self.current_template_id.unpost()

    def draft2current_values(self):
        return {'state': 'current'}

    @api.multi
    def draft2current(self):
        for record in self:
            record.post()
            record.write(self.draft2current_values())
        return True

    def current2superseded_values(self):
        return {'state': 'superseded'}

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
            record.write(self.current2superseded_values())

    def _generate_activity_definition(self):
        activity_obj = self.env['workflow.activity.definition']
        activities = activity_obj
        for r in self.filtered(lambda r: not r.activity_definition_ids):
            activity = activity_obj.create(r._activity_definition_vals())
            activity.activate()
            activities |= activity
        return activities

    def _activity_definition_vals(self):
        return {
            'type_id': self.env.ref('medical_workflow.medical_workflow').id,
            'name': self.name,
            'model_id': self.env.ref(
                'medical_document.model_medical_document_reference').id,
            'document_type_id': self.id,
        }

    @api.multi
    def generate_activity_definition(self):
        activites = self._generate_activity_definition()
        action = self.env.ref(
            'medical_workflow.workflow_activity_definition_action')
        result = action.read()[0]
        if len(activites) > 1:
            result['domain'] = "[('id', 'in', " + str(activites.ids) + ")]"
        elif len(activites) == 1:
            res = self.env.ref('workflow.activity.definition', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = activites.id
        return result


class MedicalDocumentTypeLang(models.Model):
    _name = 'medical.document.type.lang'
    _inherit = 'medical.document.language'
    _rec_name = 'lang'

    document_type_id = fields.Many2one(
        'medical.document.type',
        required=True
    )
    text = fields.Html(sanitize=True)

    _sql_constraints = [
        ('unique_language',
         'UNIQUE(lang, document_type_id)',
         'The language is allowed only once on a type.')
    ]

    def get_document_template_lang_vals(self):
        return {
            'text': self.text,
            'lang': self.lang,
        }

    @api.multi
    def preview(self):
        return self.env.ref(
            'medical_document.action_report_document_report_type'
        ).report_action(self)
