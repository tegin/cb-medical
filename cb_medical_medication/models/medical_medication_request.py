# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class MedicalMedicationRequest(models.Model):
    _inherit = 'medical.medication.request'

    location_type_id = fields.Many2one(
        'medical.location.type',
        readonly=True,
        track_visibility='onchange',
    )

    def _get_event_values(self):
        res = super()._get_event_values()
        if self.env.context.get('product_id', False):
            res['product_id'] = self.env.context.get('product_id')
            res['product_uom_id'] = self.env.context.get('product_uom_id')
            res['qty'] = self.env.context.get('qty', 1)
            res['amount'] = self.env.context.get('amount', 0)
        return res

    def _add_medication_item(self, item):
        if self.state == 'draft':
            self.draft2active()
        administration = self.with_context(
            product_id=item.product_id.id,
            product_uom_id=item.product_id.uom_id.id,
            qty=item.qty,
            amount=item.price * item.qty
        ).generate_event()
        administration.location_id = item.location_id
        administration.preparation2in_progress()
        administration.in_progress2completed()
        return administration
