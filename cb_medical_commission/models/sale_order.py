# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def recompute_lines_agents(self):
        # Commission on medical sale orders will not be managed by the
        # recompute function
        return super(
            SaleOrder, self.filtered(lambda r: not r.encounter_id)
        ).recompute_lines_agents()
