# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    practitioner_condition_ids = fields.One2many(
        "medical.practitioner.condition",
        inverse_name="practitioner_id",
        copy=False,
    )
