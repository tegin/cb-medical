# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.multi
    def unlink(self):
        sale_lines = self.mapped("sale_line_ids")
        res = super(AccountInvoiceLine, self).unlink()
        sale_lines.write({"preinvoice_group_id": False})
        return res
