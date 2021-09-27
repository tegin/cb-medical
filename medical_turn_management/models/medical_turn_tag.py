# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class MedicalTurnTag(models.Model):

    _name = "medical.turn.tag"
    _description = "Medical Turn Tag"

    name = fields.Char(required=True)

    _sql_constraints = [
        ("name_uniq", "unique(name)", _("Name and code must be unique")),
    ]
