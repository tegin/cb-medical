# Copyright 2023 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class QueueTokenLocation(models.Model):

    _inherit = "queue.token.location"
    request_group_ids = fields.One2many(
        "medical.request.group", inverse_name="queue_token_location_id"
    )
    patient_id = fields.Many2one(
        "medical.patient", store=True, compute="_compute_encounter"
    )
    encounter_id = fields.Many2one(
        "medical.encounter", store=True, compute="_compute_encounter"
    )
    encounter_identifier = fields.Char(related="encounter_id.internal_identifier")
    request_group_count = fields.Integer(compute="_compute_request_group_count")
    payor_id = fields.Many2one("res.partner", compute="_compute_payor")

    @api.depends("request_group_ids")
    def _compute_payor(self):
        for record in self:
            record.payor_id = record.request_group_ids.payor_id[:1]

    @api.depends("token_id.encounter_ids")
    def _compute_encounter(self):
        for record in self:
            encounter = record.token_id.encounter_ids
            if not encounter or len(encounter) > 1:
                record.patient_id = False
                record.encounter_id = False
                continue
            record.patient_id = encounter.patient_id
            record.encounter_id = encounter

    @api.depends("request_group_ids")
    def _compute_request_group_count(self):
        for record in self:
            record.request_group_count = len(record.request_group_ids)

    def view_encounter(self):
        self.ensure_one()
        encounter = self.request_group_ids.encounter_id
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
