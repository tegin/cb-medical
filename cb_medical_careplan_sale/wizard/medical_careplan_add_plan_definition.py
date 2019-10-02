# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class MedicalCareplanAddPlanDefinition(models.TransientModel):
    _inherit = "medical.careplan.add.plan.definition"

    qty = fields.Integer(default=1)

    def _get_values(self):
        values = super()._get_values()
        values["sub_payor_id"] = self.careplan_id.sub_payor_id.id
        values["invoice_group_method_id"] = (
            self.authorization_method_id.invoice_group_method_id.id or False
        )
        values["qty"] = self.qty
        return values
