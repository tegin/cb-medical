# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class MedicalMedicationRequest(models.Model):
    _inherit = 'medical.medication.request'

    def _get_event_values(self):
        res = super()._get_event_values()
        if self._context.get('product_id', False):
            res['product_id'] = self._context.get('product_id')
            res['product_uom_id'] = self._context.get('product_uom_id')
            res['qty'] = self._context.get('qty', 1)
        return res
