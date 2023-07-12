# Copyright 2023 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class MedicalEncounter(models.Model):

    _inherit = "medical.encounter"

    # Make it selection? Or just text of whatever?
    medical_process_description = fields.Text(string="Medical Process Description")

    def medical_impresion_tree_view_action(self):
        self.ensure_one()
        view_id = self.env.ref(
            "medical_clinical_impression.medical_clinical_impression_tree_view"
        ).id
        ctx = dict(self._context)
        ctx["default_patient_id"] = self.id

        return {
            "type": "ir.actions.act_window",
            "res_model": "medical.clinical.impression",
            "name": _("Medical Impression"),
            "view_type": "list",
            "view_mode": "tree",
            "views": [(view_id, "list")],
            "context": ctx,
            "domain": [("encounter_id", "=", self.id)],
        }
