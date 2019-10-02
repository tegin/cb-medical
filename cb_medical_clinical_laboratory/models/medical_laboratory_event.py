# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class MedicalLaboratoryEvent(models.Model):
    _inherit = "medical.laboratory.event"

    delay = fields.Date()
    laboratory_code = fields.Char(required=True, readonly=True)
    laboratory_service_id = fields.Many2one(
        "medical.laboratory.service",
        readonly=True,
        states={
            "preparation": [("readonly", False)],
            "in-progress": [("readonly", False)],
        },
    )

    @api.constrains("laboratory_code", "laboratory_service_id")
    def _check_code(self):
        if self.filtered(
            lambda r: (
                r.laboratory_service_id
                and r.laboratory_service_id.laboratory_code
                != r.laboratory_code
            )
        ):
            raise ValidationError(_("Code must be the same"))

    @api.onchange("laboratory_service_id")
    def _onchange_laboratory_service(self):
        for rec in self:
            rec.laboratory_code = rec.laboratory_service_id.laboratory_code
            cov = (
                rec.laboratory_request_id.careplan_id.coverage_id.coverage_template_id
            )
            price = rec.laboratory_service_id.service_price_ids.filtered(
                lambda r: r.laboratory_code == cov.laboratory_code
            )
            cai = self.env["medical.coverage.agreement.item"].get_item(
                self.service_id, cov, self.laboratory_request_id.center_id
            )
            if (
                rec.laboratory_service_id
                in rec.laboratory_request_id.laboratory_service_ids
            ):
                rec.is_sellable_insurance = False
                rec.is_sellable_private = False
                rec.coverage_amount = 0
                rec.coverage_cost = 0
                rec.private_amount = 0
                rec.private_cost = 0
            elif price and cai:
                if cai.coverage_percentage > 0:
                    rec.is_sellable_insurance = True
                    rec.coverage_amount = (
                        price.amount * cai.coverage_percentage / 100
                    )
                    rec.coverage_cost = (
                        price.cost * cai.coverage_percentage / 100
                    )
                else:
                    rec.is_sellable_insurance = False
                    rec.coverage_cost = 0
                    rec.coverage_amount = 0
                if cai.coverage_percentage < 100:
                    rec.is_sellable_private = True
                    rec.private_amount = (
                        price.amount * (100 - cai.coverage_percentage) / 100
                    )
                    rec.private_cost = (
                        price.cost * (100 - cai.coverage_percentage) / 100
                    )
                else:
                    rec.is_sellable_private = False
                    rec.private_amount = 0
                    rec.private_cost = 0
            elif rec.laboratory_service_id:
                raise ValidationError(_("Laboratory service is not covered."))
