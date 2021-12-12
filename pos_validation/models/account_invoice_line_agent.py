# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountInvoiceLineAgent(models.Model):

    _inherit = "account.invoice.line.agent"

    def action_settlement_invoice(self):
        self.ensure_one()
        invoices = (
            self.agent_line.mapped("settlement_id")
            .filtered(lambda r: r.state != "cancel")
            .mapped("invoice_line_ids.move_id")
        )
        if not invoices:
            return
        if len(invoices) == 1:
            return invoices.get_formview_action()
        action = self.env.ref("account.action_move_in_invoice_type").read()[0]
        action["domain"] = [("id", "in", self.ids)]
        return action
