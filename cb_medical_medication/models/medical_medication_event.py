from odoo import models


class MedicalMedicationEvent(models.Model):
    _inherit = 'medical.medication.event'

    def _get_procurement_group(self):
        if self.encounter_id:
            if not self.encounter_id.procurement_group_id:
                self.encounter_id.procurement_group_id = self.env[
                    'procurement.group'
                ].create(self.encounter_id._get_procurement_group_values())
            return self.encounter_id.procurement_group_id
        return super()._get_procurement_group()
