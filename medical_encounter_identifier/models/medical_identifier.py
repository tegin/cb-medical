from odoo import api, models


class MedicalCBIdentifier(models.AbstractModel):
    _name = "medical.cb.identifier"
    _description = "medical.cb.identifier"

    @api.model
    def get_request_format(self):
        return self.env["ir.config_parameter"].sudo().get_param("medical.identifier")

    @api.model
    def _get_cb_internal_identifier(self, vals):
        encounter_code = vals.get("encounter_id", False) or self.env.context.get(
            "default_encounter_id"
        )
        if encounter_code:
            encounter = self.env["medical.encounter"].browse(encounter_code)
            sequence = encounter.get_next_number_cb(self.get_request_format())
            return "{}-{}".format(encounter.internal_identifier, sequence)
        return False
