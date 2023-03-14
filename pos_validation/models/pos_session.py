# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import ast

from odoo import _, api, fields, models


class PosSession(models.Model):
    _inherit = "pos.session"

    validation_status = fields.Selection(
        [
            ("draft", "Draft"),
            ("in_progress", "In progress"),
            ("finished", "Finished"),
        ],
        default="draft",
        required=True,
    )
    invoice_ids = fields.One2many("account.move", compute="_compute_invoices")
    sale_order_line_ids = fields.One2many(
        "sale.order.line", inverse_name="pos_session_id", readonly=1
    )
    down_payment_ids = fields.One2many("sale.order", compute="_compute_down_payments")
    request_group_ids = fields.One2many(
        "medical.request.group", compute="_compute_lines"
    )
    procedure_request_ids = fields.One2many(
        "medical.procedure.request", compute="_compute_lines"
    )
    procedure_ids = fields.Many2many("medical.procedure", compute="_compute_lines")
    encounter_non_validated_count = fields.Integer(
        compute="_compute_encounter_non_validated_count"
    )

    @api.depends("encounter_ids", "encounter_ids.validation_status")
    def _compute_encounter_non_validated_count(self):
        for rec in self:
            rec.encounter_non_validated_count = len(
                rec.encounter_ids.filtered(lambda r: r.validation_status != "finished")
            )

    @api.depends(
        "sale_order_ids",
        "sale_order_ids.coverage_agreement_id",
        "sale_order_ids.invoice_ids",
    )
    def _compute_invoices(self):
        for record in self:
            record.invoice_ids = record.sale_order_ids.filtered(
                lambda r: not r.coverage_agreement_id
            ).mapped("invoice_ids")

    @api.depends("sale_order_ids.is_down_payment")
    def _compute_down_payments(self):
        for record in self:
            record.down_payment_ids = record.sale_order_ids.filtered(
                lambda r: r.is_down_payment
            )

    @api.depends(
        "sale_order_line_ids.medical_model",
        "sale_order_line_ids.medical_res_id",
        "sale_order_line_ids.procedure_ids",
    )
    def _compute_lines(self):
        for record in self:
            record.request_group_ids = self.env["medical.request.group"].browse(
                record.sale_order_line_ids.filtered(
                    lambda r: r.medical_model == "medical.request.group"
                ).mapped("medical_res_id")
            )
            record.procedure_request_ids = self.env["medical.procedure.request"].browse(
                record.sale_order_line_ids.filtered(
                    lambda r: r.medical_model == "medical.procedure.request"
                ).mapped("medical_res_id")
            )
            record.procedure_ids = record.sale_order_line_ids.mapped("procedure_ids")

    def action_pos_session_close(self):
        #  Unfinished encounter should be taken of the session
        self.encounter_ids.filtered(lambda r: r.state != "finished").write(
            {"pos_session_id": False}
        )
        res = super(PosSession, self).action_pos_session_close()
        self.write({"validation_status": "in_progress"})
        if not self.encounter_ids:
            self.action_validation_finish()
        return res

    def action_validation_finish(self):
        self.ensure_one()
        self.write({"validation_status": "finished"})

    def open_validation_encounter(self, barcode):
        self.ensure_one()
        encounter = self.env["medical.encounter"].search(
            [
                ("internal_identifier", "=", barcode),
                ("pos_session_id", "=", self.id),
            ]
        )
        if not encounter:
            result = self.env["ir.actions.act_window"]._for_xml_id(
                "barcode_action.barcode_action_action"
            )
            result["context"] = self.env.context.copy()
            result["context"].update(
                {
                    "default_model": "pos.session",
                    "default_method": "open_validation_encounter",
                    "default_session_id": self.id,
                    "default_status": _("Encounter %s cannot be found") % barcode,
                    "default_state": "warning",
                }
            )
            return result
        if self.env.context.get("refresh_view", False):
            return {"type": "ir.actions.act_client_load_new", "res_id": encounter.id}
        result = self.env["ir.actions.act_window"]._for_xml_id(
            "medical_administration_encounter.medical_encounter_action"
        )
        res = self.env.ref("medical_encounter.medical_encounter_form", False)
        if isinstance(result["context"], str):
            result["context"] = ast.literal_eval(result["context"])
        result["context"]["from_barcode_reader"] = True
        result["views"] = [(res and res.id or False, "form")]
        result["res_id"] = encounter.id
        return result

    def action_view_non_validated_encounters(self):
        self.ensure_one()
        result = self.env["ir.actions.act_window"]._for_xml_id(
            "medical_administration_encounter.medical_encounter_action"
        )
        result["domain"] = [
            ("pos_session_id", "=", self.id),
            ("validation_status", "!=", "finished"),
        ]
        encounters = self.encounter_ids.filtered(
            lambda r: r.validation_status != "finished"
        )
        if len(encounters) == 1:
            result["views"] = [(False, "form")]
            result["res_id"] = encounters.id
        return result
