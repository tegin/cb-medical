# Copyright 2022 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MedicalProductRequestOrder(models.Model):

    _inherit = "medical.product.request.order"

    # TODO: remember to remove company from the sequence at cb_internal_identifier

    expected_dispensation_date = fields.Date(
        default=fields.Date.today(), string="Exp. Dispensation"
    )

    center_id = fields.Many2one(
        "res.partner",
        required=True,
        domain=[("is_center", "=", True)],
        compute="_compute_center_id",
    )
    in_patient = fields.Boolean(compute="_compute_in_patient")

    @api.depends("category")
    def _compute_in_patient(self):
        for record in self:
            record.in_patient = record.category == "inpatient"

    def _complete_change_state(self):
        res = super()._complete_change_state()
        date = self.expected_dispensation_date
        if not date:
            date = fields.Date.today()
        res["expected_dispensation_date"] = date
        return res

    @api.depends("encounter_id")
    def _compute_center_id(self):
        for rec in self:
            if rec.encounter_id and rec.encounter_id.center_id:
                rec.center_id = rec.encounter_id.center_id.id
            else:
                param_obj = self.env["ir.config_parameter"].sudo()
                param_id = int(
                    param_obj.get_param("cb.prescription_default_center_id", False)
                )
                rec.center_id = self.env["res.partner"].browse(param_id)
