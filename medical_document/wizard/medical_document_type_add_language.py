from odoo import api, fields, models


class MedicalDocumentTypeAddLanguage(models.TransientModel):
    _name = "medical.document.type.add.language"
    _description = "medical document type add language"

    document_type_id = fields.Many2one(
        "medical.document.type", required=True, readonly=True
    )
    lang_ids = fields.Many2many("res.lang", compute="_compute_lang_ids")
    lang_id = fields.Many2one(
        "res.lang",
        "Language",
        required=True,
        domain="[('id', 'in', lang_ids)]",
    )

    @api.depends("document_type_id")
    def _compute_lang_ids(self):
        for res in self:
            res.lang_ids = self.env["res.lang"].search(
                [
                    ("active", "=", True),
                    (
                        "code",
                        "not in",
                        res.document_type_id.lang_ids.mapped("lang"),
                    ),
                ]
            )

    def _document_type_vals(self):
        return {
            "lang": self.lang_id.code,
            "document_type_id": self.document_type_id.id,
        }

    def run(self):
        self.ensure_one()
        self.env["medical.document.type.lang"].create(self._document_type_vals())
