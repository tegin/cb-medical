# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class WizardMedicalEncounterAddAmount(models.TransientModel):
    _name = "wizard.medical.encounter.add.amount"
    _description = 'wizard.medical.encounter.add.amount'

    def _default_product(self):
        product_id = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("sale.default_deposit_product_id")
        )
        if not product_id:
            raise ValidationError(
                _(
                    "Please define a default deposit product for advance "
                    "payments in the system configuration parameters."
                )
            )
        return self.env["product.product"].browse(product_id)

    pos_session_id = fields.Many2one(
        comodel_name="pos.session",
        string="PoS Session",
        required=True,
        domain=[("state", "=", "opened")],
    )
    partner_invoice_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner invoice",
        domain=[("customer", "=", True)],
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        related="pos_session_id.config_id.company_id",
        readonly=True,
    )
    journal_ids = fields.Many2many(
        comodel_name="account.journal",
        related="pos_session_id.journal_ids",
        readonly=True,
    )
    journal_id = fields.Many2one(
        comodel_name="account.journal",
        string="Journal",
        required=True,
        domain="[('id', 'in', journal_ids)]",
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        related="journal_id.currency_id",
        readonly=True,
    )
    product_id = fields.Many2one(
        comodel_name="product.product", default=_default_product
    )
    amount = fields.Monetary(currency_field="currency_id")
    encounter_id = fields.Many2one(
        comodel_name="medical.encounter",
        string="encounter",
        readonly=True,
        required=True,
    )

    @api.onchange("pos_session_id")
    def _onchange_pos_session_id(self):
        for record in self:
            record.account_bank_statement_id = False

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

    @api.multi
    def run(self):
        self._run()

    def _run(self):
        self.ensure_one()
        if self.amount == 0:
            raise ValidationError(_("Amount cannot be zero"))
        if not self.encounter_id.company_id:
            self.encounter_id.company_id = self.company_id
        order = self.env["sale.order"].create(self.sale_order_vals())
        line = (
            self.env["sale.order.line"]
            .with_context(force_company=order.company_id.id)
            .create(self.sale_order_line_vals(order))
        )
        line.change_company_id()
        order.with_context(force_company=order.company_id.id).action_confirm()
        invoice_ids = order.with_context(
            force_company=order.company_id.id
        ).action_invoice_create()
        invoice = self.env["account.invoice"].browse(invoice_ids)
        invoice.ensure_one()
        invoice.action_invoice_open()
        process = (
            self.env["cash.invoice.out"]
            .with_context(
                active_ids=self.pos_session_id.ids, active_model="pos.session"
            )
            .create(
                {
                    "journal_id": self.journal_id.id,
                    "invoice_id": invoice.id,
                    "amount": self.amount,
                }
            )
        )
        process.run()
        return invoice
