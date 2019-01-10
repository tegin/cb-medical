# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api,  models


class MedicalEncounterAddCareplan(models.TransientModel):
    _inherit = 'medical.encounter.add.careplan'

    @api.model
    def get_encounter_states(self):
        res = super().get_encounter_states()
        if self.env.context.get('on_validation', False):
            res.append('finished')
        return res
