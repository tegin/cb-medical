
# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MedicalEncounter(models.Model):
    _inherit = 'medical.encounter'

    center_id = fields.Many2one(
        'res.partner',
        domain=[('is_center', '=', True)],
        required=True,
        track_visibility=True,
    )
    location_id = fields.Many2one(
        required=False, default=False, invisible=1
    )

    @api.model
    def _get_internal_identifier(self, vals):
        center = self.env['res.partner'].browse(
            vals.get('center_id', False))
        if center and center.encounter_sequence_id:
            return center.encounter_sequence_id._next()
        return super()._get_internal_identifier(vals)
