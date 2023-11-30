# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, fields, models
from odoo.exceptions import ValidationError


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
