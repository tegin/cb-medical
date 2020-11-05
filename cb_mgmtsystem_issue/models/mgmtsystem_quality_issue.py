# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class MgmtsystemQualityIssue(models.Model):

    _name = "mgmtsystem.quality.issue"
    _description = "Mgmtsystem Quality Issue"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char()
    description = fields.Text("Description", required=True)
    partner_id = fields.Many2one("res.partner", "Partner", required=True)
    ref = fields.Char("Related to", readonly=True, copy=False, default="/")

    responsible_user_id = fields.Many2one(
        "res.users", "Responsible", required=True, track_visibility="onchange"
    )
    manager_user_id = fields.Many2one(
        "res.users", "Manager", required=True, track_visibility="onchange"
    )

    user_id = fields.Many2one(
        "res.users",
        "Filled in by",
        required=True,
        default=lambda self: self.env.user,
        track_visibility="onchange",
    )

    origin_ids = fields.Many2many(
        "mgmtsystem.nonconformity.origin", required=True
    )

    state = fields.Selection(
        selection=[
            ("pending", "Pending to Evaluate"),
            ("ok", "Accepted"),
            ("no_ok", "Non Conformity"),
        ],
        default="pending",
        readonly=True,
        track_visibility="onchange",
    )

    non_conformity_id = fields.Many2one(
        "mgmtsystem.nonconformity", readonly=True
    )

    @api.model
    def create(self, vals):
        if vals.get("ref", "/") == "/":
            sequence = self.env.ref("cb_mgmtsystem_issue.seq_mgmtsystem_issue")
            vals["ref"] = sequence.next_by_id()
        return super().create(vals)

    @api.multi
    def to_accepted(self):
        self.write({"state": "ok"})

    def _create_non_conformity_vals(self):
        return {
            "name": self.name,
            "description": self.description,
            "partner_id": self.partner_id.id,
            "responsible_user_id": self.responsible_user_id.id,
            "manager_user_id": self.manager_user_id.id,
            "origin_ids": [(6, 0, self.origin_ids.ids)],
        }

    @api.multi
    def to_nonconformity(self):
        self.ensure_one()
        vals = self._create_non_conformity_vals()
        non_conformity = self.env["mgmtsystem.nonconformity"].create(vals)
        message = _("Generated from issue %s") % self.ref
        non_conformity.message_post(
            body=message, subtype_id=self.env.ref("mail.mt_note").id
        )
        action = {
            "type": "ir.actions.act_window",
            "name": self.name,
            "res_model": "mgmtsystem.nonconformity",
            "res_id": non_conformity.id,
            "view_mode": "form",
        }
        self.write({"state": "no_ok", "non_conformity_id": non_conformity.id})
        return action

    @api.multi
    def back_to_pending(self):
        self.write({"state": "pending"})
