# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.fs_file import fields as fs_fields


class MedicalDiagnosticReport(models.Model):
    _inherit = "medical.diagnostic.report"

    with_department = fields.Boolean(default=False)
    medical_department_header = fields.Html(readonly=True)
    signature_id = fields.Many2one("res.users.signature", readonly=True)
    occurrence_date = fields.Datetime(related="encounter_id.create_date")
    encounter_id = fields.Many2one(readonly=True)
    image_ids = fields.One2many(
        "medical.diagnostic.report.image",
        inverse_name="diagnostic_report_id",
        copy=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )

    def _generate_serializer(self):
        result = super(MedicalDiagnosticReport, self)._generate_serializer()
        if self.with_department:
            result.update({"medical_department_header": self.medical_department_header})
        if self.image_ids:
            result.update(
                {"images": [image._generate_serializer() for image in self.image_ids]}
            )
        if self.signature_id:
            result.update({"signature_id": self.signature_id.id})
        return result

    def registered2final_change_state(self):
        res = super().registered2final_change_state()
        if not self.medical_department_id.without_practitioner:
            res["signature_id"] = self.env.user.current_signature_id.id
        return res

    def copy_action(self):
        self.ensure_one()
        result = self.copy()
        return result.get_formview_action()

    def _add_image_attachment_vals(self, name=None, datas=None, **kwargs):
        return {
            "diagnostic_report_id": self.id,
            "file": {
                "filename": name,
                "content": datas,
            },
        }

    def add_image_attachment(self, name=None, datas=None, **kwargs):
        self.ensure_one()
        if self.fhir_state != "registered":
            raise ValidationError(_("State must be registered"))
        self.env["medical.diagnostic.report.image"].create(
            self._add_image_attachment_vals(name=name, datas=datas, **kwargs)
        )
        return True

    def _get_image_grouped(self):
        self.ensure_one()
        lst = self.image_ids.ids
        n = 2
        return [
            self.env["medical.diagnostic.report.image"].browse(lst[i : i + n])
            for i in range(0, len(lst), n)
        ]


class MedicalDiagnosticReportImage(models.Model):
    _name = "medical.diagnostic.report.image"
    _description = "image for a diagnostic report"
    _order = "sequence,id"

    sequence = fields.Integer(default=20)
    diagnostic_report_id = fields.Many2one("medical.diagnostic.report", required=True)
    file = fs_fields.FSFile()
    image = fields.Image(compute="_compute_image")
    description = fields.Text()

    @api.model_create_multi
    def create(self, mvals):
        return super(
            MedicalDiagnosticReportImage,
            self.with_context(storage_location=self._get_default_backend_code()),
        ).create(mvals)

    def _get_default_backend_code(self):
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("storage.diagnostic.report.image.backend_code")
        )

    def _generate_serializer(self):
        return {
            "description": self.description,
            "image_hash": self.file.attachment.checksum,
        }

    @api.depends("file")
    def _compute_image(self):
        for record in self:
            if record.file:
                record.image = base64.b64encode(record.file.getvalue())
            else:
                record.image = False
