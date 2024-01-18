# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class LaboratoryRequest(models.Model):
    _inherit = "medical.laboratory.request"

    def get_sale_order_query(self):
        query = super().get_sale_order_query()
        query += self.mapped("laboratory_event_ids").get_sale_order_query()
        return query
