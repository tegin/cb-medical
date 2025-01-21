# Copyright 2016 Nicola Malcontenti - Agile Business Group
# Copyright 2016 Davide Corio - Abstract
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html

from odoo import models


class CommissionLineMixin(models.AbstractModel):
    _inherit = "commission.line.mixin"

    def _get_commission_amount(self, commission, subtotal, product, quantity):
        """Get the commission amount for the data given. To be called by
        compute methods of children models.
        """
        self.ensure_one()
        if (
            not product.commission_free
            and commission
            and commission.commission_type == "medical"
        ):
            result = 0
            procedures = self.procedure_id.filtered(lambda r: r.fhir_state != "aborted")
            events = self.laboratory_event_id.filtered(
                lambda r: r.fhir_state != "aborted"
            )
            requests = self.laboratory_request_id.filtered(
                lambda r: r.fhir_state != "cancelled"
            )
            if self.object_id._name == "sale.order.line":
                if procedures:
                    variable_fee = sum(procedures.mapped("variable_fee"))
                    fixed_fee = sum(procedures.mapped("fixed_fee"))
                    result += (
                        variable_fee / 100 * self.object_id.price_subtotal
                    ) + fixed_fee * self.object_id.product_uom_qty
                if events:
                    result += sum(
                        events.mapped(
                            "coverage_cost"
                            if self.object_id.order_id.coverage_agreement_id
                            else "private_cost"
                        )
                    )
                if requests:
                    variable_fee = sum(requests.mapped("variable_fee"))
                    fixed_fee = sum(requests.mapped("fixed_fee"))
                    result += (
                        variable_fee / 100 * self.object_id.price_subtotal
                    ) + fixed_fee * self.object_id.product_uom_qty
            if self.object_id._name == "account.move.line":
                if procedures:
                    variable_fee = sum(procedures.mapped("variable_fee"))
                    fixed_fee = sum(procedures.mapped("fixed_fee"))
                    result += (
                        variable_fee / 100 * self.object_id.price_subtotal
                    ) + fixed_fee * self.object_id.quantity
                if events:
                    result += sum(
                        events.mapped(
                            "coverage_cost"
                            if self.object_id.sale_line_ids.order_id.coverage_agreement_id
                            else "private_cost"
                        )
                    )
                if requests:
                    variable_fee = sum(requests.mapped("variable_fee"))
                    fixed_fee = sum(requests.mapped("fixed_fee"))
                    result += (
                        variable_fee / 100 * self.object_id.price_subtotal
                    ) + fixed_fee * self.object_id.quantity
            return result
        return super()._get_commission_amount(commission, subtotal, product, quantity)
