from odoo import models


class MedicalEncounter(models.Model):
    _inherit = "medical.encounter"

    def inprogress2onleave(self):
        self._blocking_childs()
        return super().inprogress2onleave()

    def _blocking_childs(self):
        for r in self:
            r.careplan_ids._has_blocking()
