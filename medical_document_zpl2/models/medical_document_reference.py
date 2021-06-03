# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class MedicalDocumentReference(models.Model):
    _inherit = "medical.document.reference"

    def _render(self):
        if self.document_type == "zpl2":
            return self.text.encode("utf-8"), "text"
        return super()._render()

    def _get_printer_usage(self):
        if self.document_type == "zpl2":
            return "label"
        return super()._get_printer_usage()

    def render_text(self):
        if self.document_type == "zpl2":
            return self.document_type_id.label_zpl2_id.render_label(self)
        return super().render_text()
