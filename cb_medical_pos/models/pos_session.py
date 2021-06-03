# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class PosSession(models.Model):
    _inherit = "pos.session"
    _rec_name = "internal_identifier"

    internal_identifier = fields.Char(required=True, default="/")
    encounter_ids = fields.One2many(
        comodel_name="medical.encounter",
        inverse_name="pos_session_id",
        string="Encounters",
        readonly=1,
    )
    encounter_count = fields.Integer(compute="_compute_encounter_count")
    sale_order_ids = fields.One2many(
        comodel_name="sale.order",
        inverse_name="pos_session_id",
        string="Sale orders",
        readonly=1,
    )
    sale_order_count = fields.Integer(compute="_compute_sale_order_count")

    @api.depends("encounter_ids")
    def _compute_encounter_count(self):
        for record in self:
            record.encounter_count = len(record.encounter_ids)

    @api.depends("sale_order_ids")
    def _compute_sale_order_count(self):
        for record in self:
            record.sale_order_count = len(record.sale_order_ids)

    @api.model
    def get_internal_identifier(self, vals):
        config_id = vals.get("config_id") or self.env.context.get(
            "default_config_id"
        )
        if config_id:
            pos_config = self.env["pos.config"].browse(config_id)
            if pos_config.session_sequence_id:
                return pos_config.session_sequence_id.next_by_id()
        return (
            self.env["ir.sequence"].next_by_code("pos.session.identifier")
            or "/"
        )

    @api.model
    def create(self, vals):
        if vals.get("internal_identifier", "/") == "/":
            vals["internal_identifier"] = self.get_internal_identifier(vals)
        return super(
            PosSession, self.with_context(ignore_balance_start=True)
        ).create(vals)

    @api.multi
    def action_view_encounters(self):
        self.ensure_one()
        action = self.env.ref(
            "medical_administration_encounter.medical_encounter_action"
        )
        result = action.read()[0]
        result["domain"] = [("pos_session_id", "=", self.id)]
        if len(self.encounter_ids) == 1:
            result["views"] = [(False, "form")]
            result["res_id"] = self.encounter_ids.id
        return result

    @api.multi
    def action_view_sale_orders(self):
        self.ensure_one()
        action = self.env.ref("sale.action_orders")
        result = action.read()[0]
        result["domain"] = [("pos_session_id", "=", self.id)]
        if len(self.sale_order_ids) == 1:
            result["views"] = [(False, "form")]
            result["res_id"] = self.sale_order_ids.id
        return result
