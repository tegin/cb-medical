# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, _
from odoo.exceptions import ValidationError


class MedicalCareplan(models.Model):
    _inherit = 'medical.careplan'

    def _add_medication(self, location, product, qty=1):
        medication_requests = self.medication_request_ids.filtered(
            lambda r: (
                r.product_id == product.categ_id.category_product_id and
                r.state in ['draft', 'active']
            ))
        # We are adding the information on the first medication request
        for medication_request in medication_requests:
            if medication_request.state == 'draft':
                medication_request.draft2active()
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
        raise ValidationError(_(
            'Request cannot be found for category %s'
        ) % product.categ_id.display_name)

    def add_medication(self, location, product, qty=1):
        bom = self.env['mrp.bom'].sudo()._bom_find(product=product)
        if not bom or bom.type != 'phantom':
            return self._add_medication(location, product, qty)
        factor = qty / bom.product_qty
        boms, lines = bom.sudo().explode(
            product, factor, picking_type=bom.picking_type_id)
        for bom_line, line_data in lines:
            self._add_medication(
                location, line_data['product'], line_data['qty']
            )
        self._add_medication(location, product, qty)
