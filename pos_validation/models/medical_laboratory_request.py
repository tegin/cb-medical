# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class MedicalLaboratoryRequest(models.Model):
    _name = "medical.laboratory.request"
    _inherit = ["medical.laboratory.request", "medical.request"]

    def _check_cancellable(self):
        if self.mapped("laboratory_event_ids").filtered(
            lambda r: r.state != "aborted"
        ):
            return False
        return super()._check_cancellable()
