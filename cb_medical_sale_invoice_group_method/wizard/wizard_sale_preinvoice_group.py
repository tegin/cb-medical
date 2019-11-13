# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class WizardSalePreinvoiceGroup(models.TransientModel):
    _name = "wizard.sale.preinvoice.group"

    company_ids = fields.Many2many(
        comodel_name="res.company", string="Companies"
    )
    payor_ids = fields.Many2many(
        comodel_name="res.partner",
        domain=[("is_payor", "=", True)],
        string="Payors",
    )

    def run(self):
        groups = self.env["invoice.group.method"].search(
            [("invoice_by_preinvoice", "=", True)]
        )
        domain = [("preinvoice_status", "=", "to preinvoice")]
        if self.company_ids:
            domain.append(("company_id", "in", self.company_ids.ids))
        if self.payor_ids:
            partners = self.payor_ids.ids
            partners += self.payor_ids.mapped("sub_payor_ids").ids
            domain.append(("partner_id", "in", partners))
        sale_orders = self.env["sale.order"].search(domain)
        agreements = {}
        for sale_order in sale_orders:
            for line in sale_order.order_line.filtered(
                lambda r: (
                    not r.preinvoice_group_id
                    and r.invoice_group_method_id in groups
                )
                and r.qty_invoiced < r.product_uom_qty
            ):
                cov_id = sale_order.coverage_agreement_id.id or False
                partner_invoice_id = sale_order.partner_invoice_id.id
                partner_id = sale_order.partner_id.id
                group = line.invoice_group_method_id.id
                template = line.coverage_template_id.id
                company = sale_order.company_id
                if company not in agreements:
                    agreements[company] = {}
                if cov_id not in agreements[company]:
                    agreements[company][cov_id] = {}
                if partner_id not in agreements[company][cov_id]:
                    agreements[company][cov_id][partner_id] = {}
                if (
                    partner_invoice_id
                    not in agreements[company][cov_id][partner_id]
                ):
                    agreements[company][cov_id][partner_id][
                        partner_invoice_id
                    ] = {}
                if (
                    group
                    not in agreements[company][cov_id][partner_id][
                        partner_invoice_id
                    ]
                ):
                    agreements[company][cov_id][partner_id][
                        partner_invoice_id
                    ][group] = {}
                if (
                    template
                    not in agreements[company][cov_id][partner_id][
                        partner_invoice_id
                    ][group]
                ):
                    agreements[company][cov_id][partner_id][
                        partner_invoice_id
                    ][group][template] = self.env[
                        "sale.preinvoice.group"
                    ].create(
                        {
                            "agreement_id": cov_id,
                            "company_id": company.id,
                            "partner_id": partner_id,
                            "coverage_template_id": template,
                            "partner_invoice_id": partner_invoice_id,
                            "current_sequence": 0,
                            "invoice_group_method_id": group,
                        }
                    )
                line.sequence = 999999
                line.is_validated = False
                line.preinvoice_group_id = agreements[company][cov_id][
                    partner_id
                ][partner_invoice_id][group][template]
        action = self.env.ref(
            "cb_medical_sale_invoice_group_method.sale_preinvoice_group_action"
        )
        result = action.read()[0]
        return result
