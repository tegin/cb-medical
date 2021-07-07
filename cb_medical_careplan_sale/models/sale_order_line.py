# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    encounter_id = fields.Many2one(
        "medical.encounter", readonly=True, index=True
    )
    medical_model = fields.Char(index=True)
    medical_res_id = fields.Many2oneReference(
        index=True, model_field="medical_model"
    )
    invoice_group_method_id = fields.Many2one(
        "invoice.group.method", readonly=True, index=True
    )
    authorization_method_id = fields.Many2one(
        "medical.authorization.method",
        tracking=True,
        readonly=True,
        index=True,
    )
    authorization_checked = fields.Boolean(default=False, readonly=True)
    authorization_status = fields.Selection(
        [
            ("pending", "Pending authorization"),
            ("not-authorized", "Not authorized"),
            ("authorized", "Authorized"),
        ],
        readonly=True,
    )
    medical_sale_discount_id = fields.Many2one(
        "medical.sale.discount", readonly=True
    )

    def _prepare_third_party_order_line(self):
        res = super()._prepare_third_party_order_line()
        res["invoice_group_method_id"] = self.env.ref(
            "cb_medical_careplan_sale.third_party"
        ).id
        res["encounter_id"] = self.encounter_id.id or False
        return res

    def open_medical_record(self):
        action = {
            "name": _("Medical Record"),
            "type": "ir.actions.act_window",
            "res_model": self.medical_model,
            "res_id": self.medical_res_id,
            "view_mode": "form",
        }
        return action
