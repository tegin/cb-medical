# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class MedicalMedicationRequest(models.Model):
    _inherit = 'medical.medication.request'

    def check_is_billable(self):
        return self.is_billable
