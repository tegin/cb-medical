# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def unlink(self):
        sale_lines = self.mapped("sale_line_ids")
        res = super().unlink()
        sale_lines.write({"preinvoice_group_id": False})
        return res
