from odoo import api, fields, models


class MedicalDocumentLanguage(models.AbstractModel):
    _name = "medical.document.language"

    @api.model
    def _get_languages(self):
        return self.env["res.lang"].get_installed()

    lang = fields.Selection(_get_languages, "Language", required=True)
