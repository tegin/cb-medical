# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from collections import defaultdict

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

    def action_view_sale_orders(self):
        self.ensure_one()
        action = self.env.ref("sale.action_orders")
        result = action.read()[0]
        result["domain"] = [("pos_session_id", "=", self.id)]
        if len(self.sale_order_ids) == 1:
            result["views"] = [(False, "form")]
            result["res_id"] = self.sale_order_ids.id
        return result

    def _accumulate_amount_preprocess_data(self, data):
        super(PosSession, self)._accumulate_amount_preprocess_data(data)

        def amounts():
            return {"amount": 0.0, "amount_converted": 0.0}

        third_party_receivables = defaultdict(amounts)
        inter_company_tp_receivables = defaultdict(
            lambda: defaultdict(amounts)
        )

        data.update(
            {
                "third_party_receivables": third_party_receivables,
                "inter_company_third_party_receivables": inter_company_tp_receivables,
            }
        )

    def _create_invoice_receivable_lines(self, data):
        result = super()._create_invoice_receivable_lines(data)
        inter_company_tp_receivables = result[
            "inter_company_third_party_receivables"
        ]
        invoice_receivable_lines = data["invoice_receivable_lines"]
        MoveLine = data.get("MoveLine")
        inter_company_receivable_vals = defaultdict(lambda: defaultdict(list))
        for (
            company,
            invoice_receivables,
        ) in inter_company_tp_receivables.items():
            for partner, amounts in invoice_receivables.items():
                company = data["inter_company_map"][company].company_id.id
                commercial_partner = partner.commercial_partner_id
                partner_account_id = commercial_partner.with_context(
                    force_company=company
                ).property_third_party_customer_account_id.id
                inter_company_receivable_vals[company][
                    partner_account_id
                ].append(
                    self._get_invoice_receivable_vals(
                        partner_account_id,
                        amounts["amount"],
                        amounts["amount_converted"],
                        partner=commercial_partner,
                        move=data.get("inter_company_move_map")[company],
                    )
                )
        third_party_receivables = data["third_party_receivables"]
        for partner, amounts in third_party_receivables.items():
            commercial_partner = partner.commercial_partner_id
            partner_account_id = commercial_partner.with_context(
                force_company=self.company_id.id
            ).property_third_party_customer_account_id.id
            inter_company_receivable_vals[self.company_id.id][
                partner_account_id
            ].append(
                self._get_invoice_receivable_vals(
                    partner_account_id,
                    amounts["amount"],
                    amounts["amount_converted"],
                    partner=commercial_partner,
                )
            )
        for (
            _company,
            company_receivables,
        ) in inter_company_receivable_vals.items():
            for account_id, vals in company_receivables.items():
                receivable_lines = MoveLine.create(vals)
                for receivable_line in receivable_lines:
                    if not receivable_line.reconciled:
                        if account_id not in invoice_receivable_lines:
                            invoice_receivable_lines[
                                account_id
                            ] = receivable_line
                        else:
                            invoice_receivable_lines[
                                account_id
                            ] |= receivable_line

        data.update({"invoice_receivable_lines": invoice_receivable_lines})
        return data

    def _pos_session_process_order(self, order, data):
        if not order.is_invoiced or order.account_move.is_sale_document():
            return super()._pos_session_process_order(order, data)

        key = order.partner_id
        third_party_receivables = data["third_party_receivables"]
        inter_company_tp_receivables = data[
            "inter_company_third_party_receivables"
        ]
        inter_company_amounts = data["inter_company_amounts"]
        if order.account_move.company_id == self.company_id:
            # Combine invoice receivable lines
            third_party_receivables[key] = self._update_amounts(
                third_party_receivables[key],
                {"amount": order._get_amount_receivable()},
                order.date_order,
            )
        else:
            company_id = order.account_move.company_id.id
            inter_company_tp_receivables[company_id][
                key
            ] = self._update_amounts(
                inter_company_tp_receivables[company_id][key],
                {"amount": order._get_amount_receivable()},
                order.date_order,
            )
            inter_company_amounts[company_id] = self._update_amounts(
                inter_company_amounts[company_id],
                {"amount": order._get_amount_receivable()},
                order.date_order,
            )
