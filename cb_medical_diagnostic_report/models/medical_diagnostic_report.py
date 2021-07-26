# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


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
    )

    def _generate_serializer(self):
        result = super(MedicalDiagnosticReport, self)._generate_serializer()
        if self.with_department:
            result.update(
                {"medical_department_header": self.medical_department_header}
            )
        if self.image_ids:
            result.update(
                {
                    "images": [
                        image._generate_serializer()
                        for image in self.image_ids
                    ]
                }
            )
        if self.signature_id:
            result.update({"signature_id": self.signature_id.id})
        return result

    def registered2final_change_state(self):
        res = super().registered2final_change_state()
        if not self.medical_department_id.without_practitioner:
            res["signature_id"] = self.env.user.current_signature_id.id
        return res

    def _is_editable(self):
        department = self.medical_department_id
        return super()._is_editable() and (
            not department or self.env.user in department.user_ids
        )

    @api.depends_context("uid")
    @api.depends("medical_department_id", "medical_department_id.user_ids")
    def _compute_is_editable(self):
        super()._compute_is_editable()

    def _is_cancellable(self):
        department = self.medical_department_id
        return super()._is_cancellable() and (
            not department or self.env.user in department.user_ids
        )

    @api.depends_context("uid")
    @api.depends("medical_department_id", "medical_department_id.user_ids")
    def _compute_is_cancellable(self):
        super()._compute_is_cancellable()

    def copy_action(self):
        self.ensure_one()
        result = self.copy()
        return result.get_formview_action()

    def _add_image_attachment_vals(self, name=None, datas=None, **kwargs):
        return {
            "diagnostic_report_id": self.id,
            "data": datas,
            "name": name,
        }

    def add_image_attachment(self, name=None, datas=None, **kwargs):
        self.ensure_one()
        if self.state != "registered":
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
    _inherits = {"storage.file": "file_id"}
    _order = "sequence,id"
    _default_file_type = "diagnostic_report_image"

    sequence = fields.Integer(default=20)
    diagnostic_report_id = fields.Many2one(
        "medical.diagnostic.report", required=True
    )
    file_id = fields.Many2one(
        "storage.file", required=True, ondelete="cascade"
    )
    description = fields.Text()

    @api.model
    def create(self, vals):
        vals["file_type"] = self._default_file_type
        if not vals.get("backend_id", False):
            vals["backend_id"] = self._get_default_backend_id()
        return super().create(vals)

    def _get_default_backend_id(self):
        return self.env["storage.backend"]._get_backend_id_from_param(
            self.env, "storage.diagnostic.report.image.backend_id"
        )

    def _generate_serializer(self):
        return {
            "description": self.description,
            "image_hash": self.checksum,
        }
