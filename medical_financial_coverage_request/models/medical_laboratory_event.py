# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class MedicalLaboratoryEvent(models.Model):
    _inherit = "medical.laboratory.event"

    def _change_authorization(self, vals, **kwargs):
        self.write(vals)
