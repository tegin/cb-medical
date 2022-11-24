# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class WizardCreateNonconformity(models.TransientModel):
    _name = "wizard.create.nonconformity"
    _description = "Create Issue"

    name = fields.Char(required=True)
    description = fields.Text(required=True)
    partner_id = fields.Many2one("res.partner", "Partner", required=True)
    origin_id = fields.Many2one(
        "mgmtsystem.nonconformity.origin",
        string="Origin",
        required=True,
        domain=[
            "|",
            ("responsible_user_id", "!=", False),
            ("manager_user_id", "!=", False),
        ],
    )

    def create_quality_issue(self):
        record = self.env[self.env.context.get("active_model")].browse(
            self.env.context.get("active_id", False)
        )
        issue = (
            self.env["mgmtsystem.quality.issue"]
            .with_context(tracking_disable=True)
            .create(
                {
                    "name": self.name,
                    "description": self.description,
                    "origin_ids": [(4, self.origin_id.id)],
                    "responsible_user_id": self.origin_id.responsible_user_id.id,
                    "manager_user_id": self.origin_id.manager_user_id.id,
                    "partner_id": self.partner_id.id,
                    "res_id": record.id,
                    "res_model": record._name,
                }
            )
        )
        partners = []
        if self.origin_id.notify_creator:
            partners = issue.user_id.partner_id.ids
        if self.origin_id.responsible_user_id:
            partners.append(self.origin_id.responsible_user_id.partner_id.id)
        if self.origin_id.manager_user_id:
            partners.append(self.origin_id.manager_user_id.partner_id.id)
        issue.message_subscribe(partners)
        issue.message_post(
            message_type="notification",
            subtype="mail.mt_comment",
            body=_("A new quality issue has been created by %s") % self.env.user.name,
        )
        return {
            "type": "ir.actions.act_window",
            "name": self.name,
            "res_model": "mgmtsystem.quality.issue",
            "res_id": issue.id,
            "view_mode": "form",
        }
