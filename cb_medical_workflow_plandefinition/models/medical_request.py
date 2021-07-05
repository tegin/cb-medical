# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MedicalRequest(models.AbstractModel):
    _inherit = "medical.request"

    is_billable = fields.Boolean(
        string="Is billable?", default=False, tracking=True
    )
    is_breakdown = fields.Boolean(default=False, tracking=True)
    third_party_bill = fields.Boolean(default=False, tracking=True)
    center_id = fields.Many2one(
        "res.partner",
        domain=[("is_center", "=", True)],
        required=True,
        tracking=True,
    )
    active = fields.Boolean(default=True)

    @api.model
    def _pass_performer(self, activity, parent, plan, action):
        return False
