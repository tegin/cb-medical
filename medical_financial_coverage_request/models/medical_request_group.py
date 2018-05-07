# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MedicalRequestGroup(models.Model):
    _inherit = 'medical.request.group'

    can_change_plan = fields.Boolean(
        compute='_compute_can_change_plan'
    )

    @api.depends('state')
    def _compute_can_change_plan(self):
        for record in self:
            record.can_change_plan = (record.state not in [
                'cancelled', 'completed'])
