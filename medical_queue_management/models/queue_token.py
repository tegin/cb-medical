# Copyright 2023 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class QueueToken(models.Model):

    _inherit = "queue.token"

    encounter_ids = fields.One2many("medical.encounter", inverse_name="queue_token_id")
    encounter_count = fields.Integer(compute="_compute_encounter_count")

    @api.depends("encounter_ids")
    def _compute_encounter_count(self):
        for record in self:
            record.encounter_count = len(record.encounter_ids)

    def view_encounter(self):
        self.ensure_one()
        encounter = self.encounter_ids
        encounter.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "medical_administration_encounter.action_encounter_medical_his"
        )
        action["res_id"] = encounter.id
        action["view_mode"] = "form"
        action["views"] = [
            (view_id, view_mode)
            for view_id, view_mode in action["views"]
            if view_mode == "form"
        ]
        return action
