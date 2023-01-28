# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class InvoiceSalesByGroup(models.TransientModel):
    _name = "invoice.sales.by.group"
    _description = "invoice.sales.by.group"

    date_to = fields.Date("Up to", required=True, default=fields.Date.today())
    invoice_group_method_id = fields.Many2one(
        string="Invoice Group Method",
        comodel_name="invoice.group.method",
        required=True,
    )
    customer_ids = fields.Many2many(comodel_name="res.partner")
    company_ids = fields.Many2many(comodel_name="res.company", string="Companies")

    def invoice_sales_by_group(self):
        domain = [
            ("invoice_status", "=", "to invoice"),
            ("state", "!=", "cancel"),
            ("date_order", "<", self.date_to),
            ("invoice_group_method_id", "=", self.invoice_group_method_id.id),
        ]
        if self.customer_ids:
            domain.append(("partner_id", "in", self.customer_ids.ids))
        companies = self.company_ids
        if not companies:
            companies = self.env["res.company"].search([])
        invoices = self.env["account.move"]
        for company in companies:
            sales = self.env["sale.order"].search(
                domain + [("company_id", "=", company.id)]
            )
            if not sales:
                continue
            invoices |= sales.with_context(active_model=sales._name)._create_invoices()
        if not invoices:
            return
        result = self.env["ir.actions.act_window"]._for_xml_id(
            "account.action_move_out_invoice_type"
        )
        result["domain"] = [("id", "in", invoices.ids)]
        if len(invoices) == 1:
            res = self.env.ref("account.move.form", False)
            result["views"] = [(res and res.id or False, "form")]
            result["res_id"] = invoices.id
        return result
