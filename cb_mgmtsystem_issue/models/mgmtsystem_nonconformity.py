# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class MgmtsystemNonconformity(models.Model):

    _inherit = "mgmtsystem.nonconformity"

    res_model = fields.Char(index=True)
    res_id = fields.Integer(index=True)
    ref = fields.Char(readonly=True, copy=False, default="/")

    @api.model
    def create(self, vals):
        if vals.get("ref", "/") == "/":
            sequence = self.env.ref(
                "mgmtsystem_nonconformity.seq_mgmtsystem_nonconformity"
            )
            vals["ref"] = sequence.next_by_id()
        return super().create(vals)

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
