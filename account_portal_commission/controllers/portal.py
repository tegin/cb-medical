from odoo import http
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


class RestrictedPortalAccount(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "commission_count" in counters:
            commission_count = (
                request.env["account.invoice.line.agent"].search_count(
                    [("agent_id", "=", request.env.user.partner_id.id)]
                )
                if request.env["account.invoice.line.agent"].check_access_rights(
                    "read", raise_exception=False
                )
                else 0
            )
            values["commission_count"] = commission_count
        return values

    @http.route(
        ["/my/invoices", "/my/invoices/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_invoices(
        self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw
    ):
        values = self._prepare_my_invoices_values(
            page, date_begin, date_end, sortby, filterby
        )

        # pager
        pager = portal_pager(**values["pager"])

        # content according to pager and archive selected
        invoices = values["invoices"](pager["offset"])
        request.session["my_invoices_history"] = invoices.ids[:100]

        values.update(
            {
                "invoices": invoices,
                "pager": pager,
            }
        )

        return request.render(
            "account_portal_commission.portal_my_invoices_restricted", values
        )

    @http.route(["/my/commissions"], type="http", auth="user", website=True)
    def portal_my_commissions(self):
        commission_grouped = request.env["account.invoice.line.agent"].read_group(
            domain=[("agent_id", "=", request.env.user.partner_id.id)],
            fields=["id", "amount:sum"],
            groupby=["settled"],
        )

        settled_commissions = 0.0
        unsettled_commissions = 0.0
        settled_commission_ids = []

        for line in commission_grouped:
            if line["settled"]:
                settled_commissions = line["amount"]
                settled_commission_ids.append(line["id"])
            elif not line["settled"]:
                unsettled_commissions = line["amount"]

        invoiced_group = request.env["commission.settlement.line"].read_group(
            domain=[
                ("invoice_agent_line_id", "in", settled_commission_ids),
                ("settlement_id.state", "=", "invoiced"),
            ],
            fields=["settled_amount:sum"],
            groupby=[],
        )

        invoiced_settlement = (
            invoiced_group[0].get("settled_amount") if invoiced_group else 0.0
        )

        paid_group = request.env["commission.settlement.line"].read_group(
            domain=[
                ("invoice_agent_line_id", "in", settled_commission_ids),
                ("settlement_id.invoice_id.payment_state", "=", "paid"),
            ],
            fields=["settled_amount:sum"],
            groupby=[],
        )
        paid_settlement = paid_group[0]["settled_amount"] if paid_group else 0.0

        values = {
            "settled_commissions": settled_commissions,
            "unsettled_commissions": unsettled_commissions,
            "invoiced_settlement": invoiced_settlement if invoiced_settlement else 0.0,
            "paid_settlement": paid_settlement if paid_settlement else 0.0,
            "currency_id": request.env.company.currency_id,
        }
        return request.render("account_portal_commission.portal_my_commissions", values)
