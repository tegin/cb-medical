# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class MedicalRequestGroup(models.Model):

    _inherit = "medical.request.group"

    @api.multi
    def check_authorization_action(self):
        result = super(MedicalRequestGroup, self).check_authorization_action()
        if (
            not self.authorization_method_id.check_required
            or not self.authorization_checked
        ):
            return result
        action = self.env.ref(
            "cb_medical_authorization."
            "medical_request_group_uncheck_authorization_act_window"
        )
        new_result = action.read()[0]
        new_result["context"] = result["context"]
        return new_result
