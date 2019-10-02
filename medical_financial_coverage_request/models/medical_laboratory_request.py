# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class MedicalLaboratoryRequest(models.Model):
    _inherit = "medical.laboratory.request"

    def _change_authorization(self, vals, **kwargs):
        res = super()._change_authorization(vals, **kwargs)
        self.mapped("laboratory_event_ids")._change_authorization(
            vals, **kwargs
        )
        return res
