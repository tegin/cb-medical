import json

from odoo import _, api, models
from odoo.tools.safe_eval import safe_eval


class MedicalEncounter(models.Model):
    _inherit = "medical.encounter"

    def find_encounter_by_barcode(self, barcode):
        encounter = self.search([("internal_identifier", "=", barcode)])
        if not encounter:
            document = self.env["medical.document.reference"].search(
                [("internal_identifier", "=", barcode)]
            )
            if document:
                encounter = document.encounter_id
        if not encounter:
            result = self.env["ir.actions.act_window"]._for_xml_id(
                "cb_medical_views.encounter_find_by_barcode"
            )
            context = safe_eval(result["context"])
            context.update(
                {
                    "default_state": "warning",
                    "default_status": _("Encounter %s cannot be found") % barcode,
                }
            )
            result["context"] = json.dumps(context)
            return result
        result = self.env["ir.actions.act_window"]._for_xml_id(
            "medical_administration_encounter.medical_encounter_action"
        )
        res = self.env.ref("medical_encounter.medical_encounter_form", False)
        result["views"] = [(res and res.id or False, "form")]
        result["res_id"] = encounter.id
        return result

    @api.depends("name", "internal_identifier")
    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, record.internal_identifier))
        return result
