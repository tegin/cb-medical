# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class MgmtsystemQualityIssue(models.Model):

    _name = "mgmtsystem.quality.issue"
    _order = "id desc"
    _description = "Mgmtsystem Quality Issue"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(required=True, string="Title")
    description = fields.Text("Description", required=True)
    partner_id = fields.Many2one("res.partner", "Partner", required=True)
    res_model = fields.Char(index=True)
    res_id = fields.Integer(index=True)
    ref = fields.Char("Related to", readonly=True, copy=False, default="/")
    active = fields.Boolean(default=True)

    responsible_user_id = fields.Many2one(
        "res.users",
        "Responsible",
        tracking=True,
    )
    manager_user_id = fields.Many2one(
        "res.users",
        "Manager",
        tracking=True,
    )

    user_id = fields.Many2one(
        "res.users",
        "Filled in by",
        required=True,
        default=lambda self: self.env.user,
        tracking=True,
    )

    origin_ids = fields.Many2many("mgmtsystem.nonconformity.origin", required=True)

    state = fields.Selection(
        selection=[
            ("pending", "Pending to Evaluate"),
            ("ok", "Accepted"),
            ("no_ok", "Non Conformity"),
        ],
        default="pending",
        readonly=True,
        tracking=True,
    )

    non_conformity_id = fields.Many2one("mgmtsystem.nonconformity", readonly=True)

    @api.model
    def create(self, vals):
        if vals.get("ref", "/") == "/":
            sequence = self.env.ref("cb_mgmtsystem_issue.seq_mgmtsystem_issue")
            vals["ref"] = sequence.next_by_id()
        return super().create(vals)

    def _message_auto_subscribe_followers(self, updated_values, default_subtype_ids):
        result = super()._message_auto_subscribe_followers(
            updated_values, default_subtype_ids
        )
        for field_name in ["responsible_user_id", "manager_user_id"]:
            if not updated_values.get(field_name):
                continue
            user = self.env["res.users"].browse(updated_values[field_name])
            result.append((user.partner_id.id, default_subtype_ids, False))
        return result

    def to_accepted(self):
        self.write({"state": "ok"})

    def _creation_subtype(self):
        return self.env.ref("cb_mgmtsystem_issue.issue_created")

    def _create_non_conformity_vals(self):
        return {
            "name": self.name,
            "description": self.description,
            "partner_id": self.partner_id.id,
            "responsible_user_id": self.responsible_user_id.id,
            "manager_user_id": self.manager_user_id.id,
            "res_model": self.res_model,
            "res_id": self.res_id,
            "origin_ids": [(6, 0, self.origin_ids.ids)],
        }

    def to_nonconformity(self):
        self.ensure_one()
        vals = self._create_non_conformity_vals()
        non_conformity = self.env["mgmtsystem.nonconformity"].create(vals)
        message = _("Generated from issue %s") % self.ref
        non_conformity.message_post(body=message, subtype_xmlid="mail.mt_note")
        action = {
            "type": "ir.actions.act_window",
            "name": self.name,
            "res_model": "mgmtsystem.nonconformity",
            "res_id": non_conformity.id,
            "view_mode": "form",
        }
        self.write({"state": "no_ok", "non_conformity_id": non_conformity.id})
        return action

    def back_to_pending(self):
        self.write({"state": "pending"})

    def access_related_item(self):
        self.ensure_one()
        if not self.res_model or self.res_model not in self.env:
            return False
        records = self.env[self.res_model].browse(self.res_id).exists()
        if not records:
            return False
        return {
            "name": _("Related Record"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": records._name,
            "res_id": records.id,
        }

    @api.onchange("origin_ids")
    def _default_manager_and_responsible_user_ids(self):
        if self.origin_ids:
            managers = self.origin_ids.mapped("manager_user_id")
            responsible = self.origin_ids.mapped("responsible_user_id")
            if not self.manager_user_id and managers:
                self.manager_user_id = managers[0].id
            if not self.responsible_user_id and responsible:
                self.responsible_user_id = responsible[0].id

    def post_change_message(self, field_value):
        user = self.env["res.users"].browse(field_value)
        for rec in self:
            rec.message_post(
                message_type="notification",
                subtype_xmlid="mail.mt_comment",
                body=_("Quality issue reassigned to %s.") % user.name,
            )

    def write(self, vals):
        res = super().write(vals)
        for field_name in ["responsible_user_id", "manager_user_id"]:
            if field_name not in vals:
                continue
            self.post_change_message(vals[field_name])
        return res
