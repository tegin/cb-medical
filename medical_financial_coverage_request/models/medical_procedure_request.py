# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class MedicalProcedureRequest(models.Model):
    _name = "medical.procedure.request"
    _inherit = ["medical.procedure.request", "medical.request"]

    @api.model
    def _pass_performer(self, activity, parent, plan, action):
        return True
