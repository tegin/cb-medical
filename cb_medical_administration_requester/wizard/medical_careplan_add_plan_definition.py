# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class MedicalCareplanAddPlanDefinition(models.TransientModel):
    _inherit = "medical.careplan.add.plan.definition"

    order_by_id = fields.Many2one(
        "res.partner", domain=[("is_requester", "=", True)]
    )

    def _get_values(self):
        values = super(MedicalCareplanAddPlanDefinition, self)._get_values()
        values["order_by_id"] = self.order_by_id.id or False
        return values
