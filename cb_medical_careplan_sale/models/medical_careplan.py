# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models

SO_OPEN = ['draft']


class MedicalCareplan(models.Model):
    _inherit = 'medical.careplan'

    @api.onchange('encounter_id')
    def _onchange_encounter(self):
        for record in self:
            record.center_id = self.encounter_id.center_id

    def get_payor(self):
        if self.sub_payor_id:
            return self.sub_payor_id.id
        return self.payor_id.id
