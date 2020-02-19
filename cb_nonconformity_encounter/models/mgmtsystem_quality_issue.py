# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MgmtsystemQualityIssue(models.Model):

    _inherit = 'mgmtsystem.quality.issue'

    encounter_id = fields.Many2one('medical.encounter', readonly=True)

    def _create_non_conformity_vals(self):
        res = super()._create_non_conformity_vals()
        res['encounter_id'] = self.encounter_id.id
        return res
