# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class MedicalRequest(models.AbstractModel):
    _inherit = 'medical.request'

    is_billable = fields.Boolean(
        string='Is billable?',
        default=False,
        track_visibility=True,
    )
    is_breakdown = fields.Boolean(
        default=False,
        track_visibility=True,
    )
    center_id = fields.Many2one(
        'res.partner',
        domain=[('is_center', '=', True)],
        required=True,
        track_visibility=True,
    )
    active = fields.Boolean(
        default=True,
    )
