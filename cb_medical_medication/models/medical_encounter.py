from odoo import api, fields, models


class MedicalEncounter(models.Model):
    _inherit = 'medical.encounter'

    medication_item_ids = fields.One2many(
        'medical.medication.item',
        inverse_name='encounter_id',
        states={
            'finished': [('readonly', True)],
            'cancelled': [('readonly', True)]
        },
    )

    def _add_medication_vals(self, location, product, qty, is_phantom):
        return {
            'encounter_id': self.id,
            'location_id': location.id,
            'product_id': product.id,
            'qty': qty,
            'price': product.list_price,
            'is_phantom': is_phantom,
        }

    def _add_medication(self, location, product, qty=1, is_phantom=False):
        return self.env['medical.medication.item'].create(
            self._add_medication_vals(location, product, qty, is_phantom))

    def add_medication(self, location, product, qty=1):
        bom = self.env['mrp.bom'].sudo()._bom_find(product=product)
        if not bom or bom.type != 'phantom':
            return self._add_medication(location, product, qty)
        factor = qty / bom.product_qty
        boms, lines = bom.sudo().explode(
            product, factor, picking_type=bom.picking_type_id)
        for bom_line, line_data in lines:
            self._add_medication(
                location, bom_line.product_id, line_data['qty']
            )
        self._add_medication(location, product, qty, is_phantom=True)

    @api.multi
    def inprogress2onleave(self):
        for item in self.medication_item_ids.filtered(
            lambda r: not r.is_phantom
        ):
            item._to_medication_request()
        return super().inprogress2onleave()

    @api.multi
    def onleave2finished(self):
        for careplan in self.careplan_ids:
            for req in careplan.medication_request_ids:
                if req.state == 'draft':
                    req.draft2active()
                if req.state == 'active':
                    req.active2completed()
        return super().onleave2finished()
