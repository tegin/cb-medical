# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class MedicalEncounter(models.Model):
    _inherit = 'medical.encounter'

    def _get_sale_order_vals(
            self, partner, agreement, third_party_partner, is_insurance
    ):
        vals = super()._get_sale_order_vals(
            partner, agreement, third_party_partner, is_insurance)
        if agreement:
            vals[
                'invoice_group_method_id'
            ] = agreement.invoice_group_method_id.id
        return vals
