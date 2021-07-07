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
    company_ids = fields.Many2many(
        comodel_name="res.company", string="Companies"
    )

    def invoice_sales_by_group(self):
        domain = [
            ("invoice_status", "=", "to invoice"),
            ("state", "!=", "cancel"),
            ("confirmation_date", "<", self.date_to),
        ]
        if self.customer_ids:
            domain.append(("partner_id", "in", self.customer_ids.ids))
        companies = self.company_ids
        if not companies:
            companies = self.env["res.company"].search([])
        invoices = []
        for company in companies:
            sales = self.env["sale.order"].search(
                domain + [("company_id", "=", company.id)]
            )
            invoices += sales.with_context(
                customers=self.customer_ids.ids,
                companies=company.ids,
                no_check_lines=True,
                cb_merge_draft_invoice=True,
            ).action_invoice_by_group_create(
                self.invoice_group_method_id, company
            )
        # view
        if not invoices:
            return
        action = self.env.ref("account.action_invoice_tree1")
        result = action.read()[0]
        if len(invoices) > 1:
            result["domain"] = "[('id', 'in', " + str(invoices) + ")]"
        elif len(invoices) == 1:
            res = self.env.ref("account.move.form", False)
            result["views"] = [(res and res.id or False, "form")]
            result["res_id"] = invoices[0]
        return result
