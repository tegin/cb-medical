from odoo import api, fields, models


class MedicalPatient(models.Model):
    _inherit = "medical.patient"

    medical_flag_ids = fields.One2many(
        "medical.flag", inverse_name="patient_id"
    )
    medical_flag_count = fields.Integer(compute="_compute_medical_flag_count")

    @api.depends("medical_flag_ids")
    def _compute_medical_flag_count(self):
        for rec in self:
            rec.medical_flag_count = len(rec.medical_flag_ids.ids)

    @api.multi
    def action_view_flags(self):
        self.ensure_one()
        action = self.env.ref(
            "medical_administration_flag.medical_flag_action"
        )
        result = action.read()[0]
        result["context"] = {"default_patient_id": self.id}
        result["domain"] = "[('patient_id', '=', " + str(self.id) + ")]"
        if len(self.medical_flag_ids) == 1:
            res = self.env.ref("medical.flag.view.form", False)
            result["views"] = [(res and res.id or False, "form")]
            result["res_id"] = self.medical_flag_ids.id
        return result
