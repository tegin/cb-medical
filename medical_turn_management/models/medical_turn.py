# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class MedicalTurn(models.Model):
    _name = "medical.turn"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date asc"
    _description = "Medical Turn"

    center_ids = fields.Many2many(
        string="Centers",
        required=True,
        comodel_name="res.partner",
        domain=[("is_center", "=", True)],
        track_visibility="onchange",
    )
    practitioner_id = fields.Many2one(
        string="Practitioner",
        comodel_name="res.partner",
        track_visibility="onchange",
    )
    specialty_id = fields.Many2one(
        "medical.turn.specialty", track_visibility="onchange", required=True
    )
    date = fields.Datetime(
        required=True,
        copy=False,
        track_visibility="onchange",
        default=lambda r: fields.Datetime.now(),
    )
    duration = fields.Float(
        "Duration (in hours)", track_visibility="onchange", required=True
    )

    @api.depends("practitioner_id", "center_ids", "specialty_id")
    def _compute_display_name(self):
        return super()._compute_display_name()

    @api.multi
    def name_get(self):
        result = []
        for rec in self:
            name = "%s [%s] (%s)" % (
                rec.specialty_id.name,
                rec.practitioner_id.display_name or _("Pending to assign"),
                ",".join([c.ref or c.name for c in rec.center_ids]),
            )
            result.append((rec.id, name))
        return result
