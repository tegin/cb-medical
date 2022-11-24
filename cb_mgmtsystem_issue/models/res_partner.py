# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    quality_issue_ids = fields.One2many(
        "mgmtsystem.quality.issue",
        inverse_name="partner_id",
    )
    quality_issue_count = fields.Integer(compute="_compute_quality_issue_count")

    @api.depends("quality_issue_ids")
    def _compute_quality_issue_count(self):
        for record in self:
            record.quality_issue_count = len(record.quality_issue_ids)

    def action_view_quality_issues(self):
        self.ensure_one()
        action = self.env.ref(
            "cb_mgmtsystem_issue.mgmtsystem_quality_issue_act_window"
        ).read()[0]
        if len(self.quality_issue_ids) > 1:
            action["domain"] = [("partner_id", "=", self.id)]
        elif self.quality_issue_ids:
            action["views"] = [
                (
                    self.env.ref(
                        "cb_mgmtsystem_issue.mgmtsystem_quality_issue_form_view"
                    ).id,
                    "form",
                )
            ]
            action["res_id"] = self.quality_issue_ids.id
        return action
