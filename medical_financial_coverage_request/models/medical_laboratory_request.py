# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class MedicalLaboratoryRequest(models.Model):
    _inherit = "medical.laboratory.request"

    coverage_percentage = fields.Float(
        related="coverage_agreement_item_id.coverage_percentage"
    )

    def _change_authorization(self, vals, **kwargs):
        res = super()._change_authorization(vals, **kwargs)
        self.mapped("laboratory_event_ids")._change_authorization(vals, **kwargs)
        return res

    def _generate_sample_vals(self):
        result = super()._generate_sample_vals()
        result["center_id"] = self.center_id.id
        return result
