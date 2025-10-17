# Copyright 2023 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import json

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


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
    info = fields.Text()
    color = fields.Char(related="group_id.color")
    action_data = fields.Char(compute="_compute_action_data")
    allows_flag = fields.Boolean(related="location_id.allows_flag")
    action_id = fields.Many2one("queue.location.action", readonly=True)
    flagged = fields.Boolean()

    @api.depends("location_id")
    def _compute_action_data(self):
        for record in self:
            actions = record.location_id.action_ids
            if record.action_id not in actions:
                actions |= record.action_id
            record.action_data = json.dumps(actions.read(["name", "icon", "color"]))

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

    def action_kanban_call(self):
        self.ensure_one()
        if self.state != "in-progress":
            raise ValidationError(_("State must be in-progress"))
        self.with_context(
            location_id=self.location_id.id, ignore_expected_location=True
        ).action_call()
        return {"type": "ir.actions.client", "tag": "soft_reload"}

    def action_kanban_leave(self):
        self.ensure_one()
        if self.state != "in-progress":
            raise ValidationError(_("State must be in-progress"))
        self.with_context(location_id=self.location_id.id).action_leave()
        return {"type": "ir.actions.client", "tag": "soft_reload"}

    def action_kanban_back_to_draft(self):
        self.ensure_one()
        if self.state != "in-progress":
            raise ValidationError(_("State must be in-progress"))
        self.with_context(location_id=self.location_id.id).action_back_to_draft()
        return {"type": "ir.actions.client", "tag": "soft_reload"}

    def action_kanban_cancel(self):
        self.ensure_one()
        self.with_context(location_id=self.location_id.id).action_cancel()
        return {"type": "ir.actions.client", "tag": "soft_reload"}

    def action_kanban_assign(self):
        self.ensure_one()
        if self.location_id and self.state == "draft":
            self.with_context(location_id=self.location_id.id).action_assign()
            self.with_context(
                location_id=self.location_id.id, ignore_expected_location=True
            ).action_call()
            return {"type": "ir.actions.client", "tag": "soft_reload"}
        return {}

    def edit_info_action(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "medical_queue_management.queue_token_location_edit_info"
        )
        action["res_id"] = self.id
        return action

    def view_patient(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "medical_base.medical_patient_his_window_action"
        )
        action["res_id"] = self.encounter_id.patient_id.id
        action["view_mode"] = "form"
        action["views"] = [
            (view_id, view_mode)
            for view_id, view_mode in action["views"]
            if view_mode == "form"
        ]
        return action

    def force_save(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_multi",
            "actions": [
                {"type": "ir.actions.act_window_close"},
                {"type": "ir.actions.client", "tag": "soft_reload"},
            ],
        }

    def assign_location_action(self):
        self.ensure_one()
        action = self.env["queue.location.action"].browse(
            self.env.context.get("action_id")
        )
        if action and action in self.location_id.action_ids:
            self.action_id = action

    def toggle_flagged(self):
        for record in self:
            record.flagged = not record.flagged

    def action_kanban_location_assign(self, location_id):
        if self.location_id.id != location_id and self.state == "in-progress":
            self._action_back_to_draft(self.location_id)
        self.with_context(location_id=location_id).action_assign()
        if not self.env.context.get("do_not_call"):
            self.with_context(
                location_id=location_id,
                ignore_expected_location=True,
            ).action_call()
