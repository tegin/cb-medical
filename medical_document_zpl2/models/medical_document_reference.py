# Copyright 2018 Creu Blanca
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class MedicalDocumentReference(models.Model):
    _inherit = 'medical.document.reference'

    def render_report(self):
        if self.document_type == 'zpl2':
            return self.text
        return super().render_report()

    def render_text(self):
        if self.document_type == 'zpl2':
            return self.document_type_id.label_zpl2_id.render_label(self)
        return super().render_text()
