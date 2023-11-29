# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_is_zero


class WizardMedicalEncounterAddAmount(models.TransientModel):
    _name = "wizard.medical.encounter.add.amount"
    _description = "wizard.medical.encounter.add.amount"

    pos_session_id = fields.Many2one(
        comodel_name="pos.session",
        string="PoS Session",
        required=True,
        domain=[("state", "=", "opened")],
    )
    partner_invoice_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner invoice",
        domain=[("customer_rank", ">", 0)],
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        related="pos_session_id.config_id.company_id",
        readonly=True,
    )
    payment_method_ids = fields.Many2many(
        "pos.payment.method",
        related="pos_session_id.config_id.payment_method_ids",
        readonly=True,
    )
    payment_method_id = fields.Many2one(
        "pos.payment.method",
        domain="[('id', 'in', payment_method_ids)]",
        required=True,
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        related="pos_session_id.currency_id",
        readonly=True,
    )
    amount = fields.Monetary(currency_field="currency_id")
    encounter_id = fields.Many2one(
        comodel_name="medical.encounter",
        string="encounter",
        readonly=True,
        required=True,
    )

    def sale_order_vals(self):
        vals = {
            "encounter_id": self.encounter_id.id,
            "partner_id": self.encounter_id.patient_id.partner_id.id,
            "patient_id": self.encounter_id.patient_id.id,
            "company_id": self.encounter_id.company_id.id,
            "pos_session_id": self.pos_session_id.id,
            "is_down_payment": True,
        }
        if self.partner_invoice_id:
            vals["partner_invoice_id"] = self.partner_invoice_id.id
        return vals

    def sale_order_line_vals(self, order):
        return {
            "order_id": order.id,
            "product_id": self.product_id.id,
            "name": self.product_id.name,
            "product_uom_qty": 1,
            "product_uom": self.product_id.uom_id.id,
            "price_unit": self.amount,
        }

    def run(self):
        self._run()

    def _run(self):
        self.ensure_one()
        if self.amount == 0:
            raise ValidationError(_("Amount cannot be zero"))
        if not self.encounter_id.company_id:
            self.encounter_id.company_id = self.company_id
        order = self.env["pos.order"].create(self._run_order_vals())
        order.add_payment(
            {
                "pos_order_id": order.id,
                "amount": order._get_rounded_amount(self.amount),
                "payment_method_id": self.payment_method_id.id,
                "encounter_id": self.encounter_id.id,
            }
        )
        order.action_pos_order_paid()
        return order

    def _run_order_vals(self):
        return {
            "amount_total": self.amount,
            "currency_id": self.currency_id.id,
            "partner_id": self.encounter_id.patient_id.partner_id.id,
            "session_id": self.pos_session_id.id,
            "encounter_id": self.encounter_id.id,
            "amount_tax": 0,
            "amount_paid": self.amount,
            "amount_return": 0,
            "is_deposit": True,
        }

    def _run_old(self):
        self.ensure_one()
        if float_is_zero(self.amount, precision_rounding=self.currency_id.rounding):
            raise ValidationError(_("Amount cannot be zero"))
        if not self.encounter_id.company_id:
            self.encounter_id.company_id = self.company_id
        order = self.env["sale.order"].create(self.sale_order_vals())
        line = (
            self.env["sale.order.line"]
            .with_company(order.company_id.id)
            .create(self.sale_order_line_vals(order))
        )
        for line2 in line:
            line2._compute_tax_id()
        # line._compute_tax_id()
        order.with_company(order.company_id.id).action_confirm()
        for line in order.order_line:
            line.qty_delivered = line.product_uom_qty
        patient_journal = order.company_id.patient_journal_id.id
        invoice_ids = (
            order.with_company(order.company_id.id)
            .with_context(
                active_model=order._name,
                default_journal_id=patient_journal,
            )
            ._create_invoices(final=True)
        )
        invoice = self.env["account.move"].browse(invoice_ids).id
        invoice.ensure_one()
        invoice.action_post()
        process = (
            self.env["pos.box.cash.invoice.out"]
            .with_context(
                active_ids=self.pos_session_id.ids, active_model="pos.session"
            )
            .create(
                {
                    "payment_method_id": self.payment_method_id.id,
                    "move_id": invoice.id,
                    "amount": self.amount,
                    "session_id": self.pos_session_id.id,
                }
            )
        )
        process.with_context(default_encounter_id=self.encounter_id.id).run()
        return invoice
