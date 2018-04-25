# Copyright 2018 Creu Blanca
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class MedicalDocumentTemplate(models.Model):
    # FHIR Entity: Document Refernece
    # (https://www.hl7.org/fhir/documentreference.html)
    _name = 'medical.document.template'
    _description = 'Medical Document Template'
    _order = 'sequence desc'

    document_type_id = fields.Many2one(
        'medical.document.type', required=True, readonly=True,
        ondelete='cascade',
    )
    sequence = fields.Integer()
    state = fields.Selection([
        ('draft', 'Draft'),
        ('current', 'Current'),
        ('superseded', 'Superseded')
    ], required=True, default='draft', readonly=True)
    text = fields.Html(sanitize=True)

    def unpost(self):
        self.state = 'superseded'

    def render_template(self, model, res_ids, post_process=False):
        return self.env['mail.template'].render_template(
            self.text, model, res_ids, post_process=post_process
        )
