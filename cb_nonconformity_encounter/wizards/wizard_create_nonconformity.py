# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class WizardCreateNonconformity(models.TransientModel):
    _name = "wizard.create.nonconformity"
    _description = "wizard.create.nonconformity"

    name = fields.Char(required=True)
    description = fields.Text(required=True)

    origin_id = fields.Many2one(
        "mgmtsystem.nonconformity.origin",
        string="Origin",
        required=True,
        domain=[("from_encounter", "=", True)],
    )

    @api.multi
    def create_quality_issue(self):
        encounter_id = self.env.context.get("active_id", False)
        encounter_id = self.env["medical.encounter"].browse(encounter_id)
        issue = self.env["mgmtsystem.quality.issue"].create(
            {
                "name": self.name,
                "description": self.description,
                "partner_id": encounter_id.patient_id.partner_id.id,
                "origin_ids": [(4, self.origin_id.id)],
                "responsible_user_id": self.origin_id.responsible_user_id.id,
                "manager_user_id": self.origin_id.manager_user_id.id,
                "encounter_id": encounter_id.id,
            }
        )
        issue.message_unsubscribe(issue.user_id.partner_id.ids)
        issue.message_subscribe(
            [
                self.origin_id.responsible_user_id.partner_id.id,
                self.origin_id.manager_user_id.partner_id.id,
            ]
        )
        action = {
            "type": "ir.actions.act_window",
            "name": self.name,
            "res_model": "mgmtsystem.quality.issue",
            "res_id": issue.id,
            "view_mode": "form",
        }
        return action
