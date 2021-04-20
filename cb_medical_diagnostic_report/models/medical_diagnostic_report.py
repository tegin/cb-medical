# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalDiagnosticReport(models.Model):

    _inherit = "medical.diagnostic.report"

    with_department = fields.Boolean(default=False)
    medical_department_header = fields.Html(readonly=True)
    signature_id = fields.Many2one("res.users.signature", readonly=True)
    occurrence_date = fields.Datetime(related="encounter_id.create_date")
    encounter_id = fields.Many2one(readonly=True)

    def _generate_serializer(self):
        result = super(MedicalDiagnosticReport, self)._generate_serializer()
        if self.with_department:
            result.update(
                {"medical_department_header": self.medical_department_header}
            )
        if self.signature_id:
            result.update({"signature_id": self.signature_id.id})
        return result

    def registered2final_change_state(self):
        res = super().registered2final_change_state()
        res["signature_id"] = self.env.user.current_signature_id.id
        return res
