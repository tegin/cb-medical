# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, _
from odoo.exceptions import ValidationError


class MedicalCareplan(models.Model):
    _inherit = 'medical.careplan'

    def add_medication(self, location, product, qty=1):
        medication_requests = self.medication_request_ids.filtered(
            lambda r: r.product_id == product.categ_id.category_product_id
        )
        # We are adding the information on the first medication request
        for medication_request in medication_requests:
            administration = medication_request.with_context(
                product_id=product.id,
                product_uom_id=product.uom_id.id,
                qty=qty or 1
            ).generate_event()
            administration.location_id = location
            administration.preparation2in_progress()
            administration.in_progress2completed()
            return administration
        # If no medications are found, we are returning an error
        raise ValidationError(_('Request cannot be found'))
