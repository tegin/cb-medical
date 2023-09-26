# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class MedicalEncounter(models.Model):
    _inherit = "medical.encounter"

    pos_session_id = fields.Many2one(
        comodel_name="pos.session",
        string="PoS Session",
        readonly=1,
        tracking=True,
    )
    pos_payment_ids = fields.One2many("pos.payment", inverse_name="encounter_id")
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        readonly=1,
        tracking=True,
    )
    currency_id = fields.Many2one(
        "res.currency", related="company_id.currency_id", readonly=True
    )
    pending_private_amount = fields.Monetary(
        currency_field="currency_id", compute="_compute_pending_private_amount"
    )
    laboratory_request_ids = fields.One2many(
        "medical.laboratory.request", inverse_name="encounter_id"
    )

    @api.depends(
        "sale_order_ids.coverage_agreement_id",
        "sale_order_ids.amount_total",
        "pos_payment_ids",
        "sale_order_ids.invoice_ids.amount_total",
    )
    def _compute_pending_private_amount(self):
        for record in self:
            inv = record.sale_order_ids.filtered(
                lambda r: not r.coverage_agreement_id and r.invoice_ids
            ).mapped("invoice_ids")
            orders = record.sale_order_ids.filtered(
                lambda r: not r.coverage_agreement_id and not r.invoice_ids
            )
            record.pending_private_amount = (
                sum(
                    inv.filtered(lambda r: r.move_type == "out_invoice").mapped(
                        "amount_total"
                    )
                )
                - sum(
                    inv.filtered(lambda r: r.move_type != "out_invoice").mapped(
                        "amount_total"
                    )
                )
                + sum(o.amount_total for o in orders)
                - sum(record.mapped("pos_payment_ids.amount"))
            )

    def _get_sale_order_vals(
        self,
        partner=False,
        coverage=False,
        agreement=False,
        third_party_partner=False,
        invoice_group_method=False,
        *kwargs
    ):
        vals = super()._get_sale_order_vals(
            partner=partner,
            coverage=coverage,
            agreement=agreement,
            third_party_partner=third_party_partner,
            invoice_group_method=invoice_group_method,
            *kwargs,
        )
        session = self.pos_session_id.id or self._context.get("pos_session_id")
        if session:
            vals["pos_session_id"] = session
        if not agreement:
            if not self.company_id.id and not self._context.get("company_id"):
                raise ValidationError(
                    _("Company is required in order to create Sale Orders")
                )
            vals["company_id"] = self.company_id.id or self._context.get("company_id")
        partner_obj = partner.with_company(vals["company_id"])
        if "payment_term_id" not in vals:
            term = partner_obj.property_payment_term_id
            if term:
                vals["payment_term_id"] = term.id
        if "fiscal_position_id" not in vals:
            position = partner_obj.property_account_position_id
            if position:
                vals["fiscal_position_id"] = position.id
        addr = partner_obj.address_get(["delivery", "invoice"])
        if "partner_invoice_id" not in vals:
            vals["partner_invoice_id"] = addr["invoice"]
        if "partner_shipping_id" not in vals:
            vals["partner_shipping_id"] = addr["delivery"]
        return vals

    def inprogress2onleave_values(self):
        res = super().inprogress2onleave_values()
        if not self.company_id:
            if not self._context.get("company_id", False):
                raise ValidationError(_("Company is required"))
            res["company_id"] = self._context.get("company_id", False)
        if self._context.get("pos_session_id", False):
            res["pos_session_id"] = self._context.get("pos_session_id", False)
        return res

    def inprogress2onleave(self):
        if self.laboratory_request_ids.filtered(
            lambda r: not r.laboratory_event_ids and r.fhir_state != "cancelled"
        ):
            raise ValidationError(_("Laboratory requests are not fulfilled."))
        self.create_sale_order()
        res = super().inprogress2onleave()
        sos = self.sale_order_ids.filtered(
            lambda r: not r.coverage_agreement_id and r.state == "draft"
        )
        if not sos or all(so.amount_total == 0 for so in sos):
            self.onleave2finished()
        return res

    def medical_encounter_close_action(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "cb_medical_pos.wizard_medical_encounter_close_action"
        )
        action["context"] = {
            "default_encounter_id": self.id,
        }
        return action

    def finish_sale_order(self, sale_order):
        if not self._context.get("pos_session_id", False):
            raise ValidationError(
                _("Payment journal is necessary in order to finish sale orders")
            )
        if sale_order.state == "draft":
            sale_order.action_confirm()
        if sale_order.invoice_status == "invoiced":
            # This was already invoiced, not managed here...
            return
        for line in sale_order.order_line:
            line.qty_delivered = line.product_uom_qty
        cash_vals = {}
        if not sale_order.third_party_order:
            model = "pos.box.cash.invoice.out"
            patient_journal = sale_order.company_id.patient_journal_id.id
            invoice = sale_order.with_context(
                default_journal_id=patient_journal,
                no_check_lines=True,
                no_split_invoices=True,
                active_model=sale_order._name,
            )._create_invoices()

            amount = invoice.amount_total
            if amount < 0:
                invoice.action_switch_invoice_into_refund_credit_note()
            invoice.action_post()
            # Invoice has been created
            if amount == 0:
                return
            cash_vals.update({"move_id": invoice.id, "amount": amount})
        else:
            model = "cash.sale.order.out"
            cash_vals.update(
                {
                    "sale_order_id": sale_order.id,
                    "amount": sale_order.amount_total,
                }
            )
        if cash_vals["amount"] != 0 and not self._context.get(
            "encounter_finish_dont_pay", False
        ):
            if not self._context.get("payment_method_id", False):
                raise ValidationError(
                    _("Payment method is necessary in order to " "finish sale orders")
                )
            payment_method_id = self._context.get("payment_method_id", False)
            pos_session_id = self._context.get("pos_session_id", False)
            cash_vals["payment_method_id"] = payment_method_id
            # We are going to pay the invoice / third party sale.order
            cash_vals["session_id"] = pos_session_id
            process = (
                self.env[model]
                .with_context(active_ids=[pos_session_id], active_model="pos.session")
                .create(cash_vals)
            )
            process.with_context(default_encounter_id=self.id).run()

    def onleave2finished_values(self):
        res = super().onleave2finished_values()
        if self._context.get("pos_session_id", False):
            res["pos_session_id"] = self._context.get("pos_session_id", False)
        return res

    def onleave2finished(self):
        for res in self.filtered(lambda r: r.state == "onleave"):
            extra_down_payment = res.sale_order_ids.filtered(
                lambda r: not r.coverage_agreement_id
                and r.state == "draft"
                and r.is_down_payment
            )
            sale_orders = res.sale_order_ids.filtered(
                lambda r: not r.coverage_agreement_id and not r.is_down_payment
            )
            if extra_down_payment:
                extra_down_payment.ensure_one()
                res.finish_sale_order(extra_down_payment)
                order = sale_orders.filtered(lambda r: not r.third_party_order)
                order.ensure_one()
                for extra_line in extra_down_payment.order_line:
                    line = order.order_line.filtered(
                        lambda r: r.down_payment_sale_line_id == extra_line
                    )
                    line.ensure_one()
                    line.write(
                        {
                            "name": extra_line._get_invoice_name(),
                            "down_payment_line_id": extra_line.invoice_lines[0].id,
                        }
                    )
            for sale_order in sale_orders:
                res.finish_sale_order(sale_order)
        return super().onleave2finished()

    def down_payment_inverse_vals(self, order, line):
        vals = {
            "order_id": order.id,
            "product_id": line.product_id.id,
            "name": line.name,
            "product_uom_qty": line.product_uom_qty,
            "product_uom": line.product_uom.id,
            "price_unit": -line.price_unit * (1.0 - line.discount / 100.0),
            "down_payment_sale_line_id": line.id,
        }
        if line.invoice_lines:
            vals.update(
                {
                    "down_payment_line_id": line.invoice_lines[0].id,
                    "name": line._get_invoice_name(),
                }
            )
        return vals

    def get_sale_order_lines(self):
        values = super().get_sale_order_lines()
        down_payments = self.sale_order_ids.filtered(lambda r: r.is_down_payment)
        if down_payments:
            key = (
                self.env["medical.coverage.agreement"],
                self.get_patient_partner(),
                self.env["medical.coverage"],
                self.env["res.partner"],
                self.env["invoice.group.method"],
            )
            if key not in values:
                values[key] = []
        return values

    def _generate_sale_order(
        self,
        order_lines,
        agreement=False,
        partner=False,
        coverage=False,
        third_party_partner=False,
        invoice_group_method=False,
        **kwargs
    ):
        order = super()._generate_sale_order(
            order_lines,
            agreement=agreement,
            partner=partner,
            coverage=coverage,
            third_party_partner=third_party_partner,
            invoice_group_method=invoice_group_method,
            **kwargs,
        )
        order.flush()
        order.order_line._compute_tax_id()
        # Ensure that the taxes are defined
        if not agreement and not third_party_partner:
            orders = self.sale_order_ids.filtered(lambda r: r.is_down_payment)
            for pay in orders:
                for line in pay.order_line:
                    inverse_line = self.env["sale.order.line"].create(
                        self.down_payment_inverse_vals(order, line)
                    )
                    for line in inverse_line:
                        line._compute_tax_id()
                    # inverse_line.change_company_id()
            # We want to avoid making negative invoices, so we will generate a
            # down_payment if it is negative
            if (
                float_compare(
                    order.amount_total,
                    0,
                    precision_rounding=order.currency_id.rounding,
                )
                == -1
            ):
                product_id = int(
                    self.env["ir.config_parameter"]
                    .sudo()
                    .get_param("sale.default_deposit_product_id")
                )
                new_order = self.env["sale.order"].create(
                    self.fix_negative_sale_order_vals()
                )
                line = (
                    self.env["sale.order.line"]
                    .with_company(order.company_id.id)
                    .create(
                        self.fix_negative_sale_order_line_vals(
                            new_order,
                            self.env["product.product"].browse(product_id),
                            order.amount_total,
                        )
                    )
                )
                for line2 in line:
                    line2._compute_tax_id()
                # line.change_company_id()
                inverse_line = self.env["sale.order.line"].create(
                    self.down_payment_inverse_vals(order, line)
                )
                for line in inverse_line:
                    line._compute_tax_id()
                # inverse_line.change_company_id()
        return order

    def fix_negative_sale_order_vals(self):
        vals = {
            "encounter_id": self.id,
            "partner_id": self.patient_id.partner_id.id,
            "patient_id": self.patient_id.id,
            "company_id": self.company_id.id,
            "pos_session_id": self._context.get("pos_session_id", False),
            "is_down_payment": True,
        }
        return vals

    def fix_negative_sale_order_line_vals(self, order, product, amount):
        return {
            "order_id": order.id,
            "product_id": product.id,
            "name": product.name,
            "product_uom_qty": 1,
            "product_uom": product.uom_id.id,
            "price_unit": amount,
        }
