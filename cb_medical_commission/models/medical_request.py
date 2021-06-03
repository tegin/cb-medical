# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class MedicalRequest(models.AbstractModel):
    _inherit = "medical.request"

    @api.model
    def get_third_party_product(self):
        return int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("cb.default_third_party_product")
        )

    def get_commission(self, amount):
        result = 0
        for procedure in self.procedure_request_ids.filtered(
            lambda r: not r.is_billable
        ).mapped("procedure_ids"):
            result += amount * procedure.variable_fee / 100
            result += procedure.fixed_fee
        return result

    def get_sale_order_line_vals(self, is_insurance):
        res = super().get_sale_order_line_vals(is_insurance)
        if self.third_party_bill:
            res["third_party_product_id"] = self.get_third_party_product()
            res["third_party_price"] = self.get_commission(res["price_unit"])
        return res
