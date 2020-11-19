# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class WizardCreateNonconformity(models.TransientModel):
    _name = "wizard.create.nonconformity"
    _description = "Create Issue"

    name = fields.Char(required=True)
    description = fields.Text(required=True)

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
                    "partner_id": record._get_quality_issue_partner().id,
                    "origin_ids": [(4, self.origin_id.id)],
                    "responsible_user_id": self.origin_id.responsible_user_id.id,
                    "manager_user_id": self.origin_id.manager_user_id.id,
                    "res_id": record.id,
                    "res_model": record._name,
                }
            )
        )
        partners = []
        if self.origin_id.responsible_user_id:
            partners.append(self.origin_id.responsible_user_id.partner_id.id)
        if self.origin_id.manager_user_id:
            partners.append(self.origin_id.manager_user_id.partner_id.id)
        issue.message_subscribe(partners)
        doc_name = self.env["ir.model"]._get(self._name).name
        issue._message_log(body=_("%s created") % doc_name)
        action = {
            "type": "ir.actions.act_window",
            "name": self.name,
            "res_model": "mgmtsystem.quality.issue",
            "res_id": issue.id,
            "view_mode": "form",
        }
        return action
