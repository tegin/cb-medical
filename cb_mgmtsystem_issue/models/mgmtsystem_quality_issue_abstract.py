# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class MgmtsystemQualityIssue(models.AbstractModel):

    _name = "mgmtsystem.quality.issue.abstract"
    _description = "Mgmtsystem Quality Issue Abstract"

    quality_issue_ids = fields.One2many(
        "mgmtsystem.quality.issue",
        inverse_name="res_id",
        domain=lambda r: [("res_model", "=", r._name)],
    )
    quality_issue_count = fields.Integer(
        compute="_compute_quality_issue_count"
    )

    @api.depends("quality_issue_ids")
    def _compute_quality_issue_count(self):
        for record in self:
            record.quality_issue_count = len(record.quality_issue_ids)

    def action_view_quality_issues(self):
        action = self.env.ref(
            "cb_mgmtsystem_issue.mgmtsystem_quality_issue_act_window"
        ).read()[0]
        if len(self.quality_issue_ids) > 1:
            action["domain"] = [("id", "in", self.quality_issue_ids.ids)]
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

    def _get_quality_issue_partner(self):
        """Hook function to be overridden if necessary"""
        if hasattr(self, "partner_id"):
            return self.partner_id
        raise Exception(
            _("Partner cannot be found for this model (%s)") % self._name
        )
