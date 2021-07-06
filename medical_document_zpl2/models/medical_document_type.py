from odoo import api, fields, models


class MedicalDocumentType(models.Model):
    # FHIR Entity: Document Refernece
    # (https://www.hl7.org/fhir/documentreference.html)
    _inherit = 'medical.document.type'

    document_type = fields.Selection(selection_add=[('zpl2', 'ZPL2 Label')])
    label_zpl2_id = fields.Many2one(
        'printing.label.zpl2',
        states={'current': [('readonly', True)]}
    )

    @api.multi
    def post(self):
        self.ensure_one()
        if self.document_type == 'zpl2':
            return
        return super().post()
