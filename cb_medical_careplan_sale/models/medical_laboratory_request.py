# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class LaboratoryRequest(models.Model):
    _inherit = 'medical.laboratory.request'

    def compute_price(self, is_insurance):
        if is_insurance:
            return sum(e.coverage_amount for e in self.laboratory_event_ids)
        return sum(e.private_amount for e in self.laboratory_event_ids)

    def get_sale_order_query(self):
        query = super().get_sale_order_query()
        query += self.mapped('laboratory_event_ids').get_sale_order_query()
        return query

    def _get_event_values(self, vals=False):
        res = super()._get_event_values(vals)
        if not res.get('authorization_status', False):
            res['authorization_status'] = self.authorization_status
        return res
