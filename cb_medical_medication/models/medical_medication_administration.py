from odoo import models


class MedicalMedicationAdministration(models.Model):
    _inherit = "medical.medication.administration"

    def _get_procurement_group_vals(self):
        res = super()._get_procurement_group_vals()
        res["encounter_id"] = self.medication_request_id.encounter_id.id
        return res
