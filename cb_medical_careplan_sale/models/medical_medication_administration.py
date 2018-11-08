# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class MedicalMedicationAdministration(models.Model):
    _inherit = 'medical.medication.administration'

    price = fields.Float()

    @api.model
    def create(self, vals):
        if 'price' not in vals:
            vals['price'] = self.env['product.product'].browse(
                vals['product_id']).list_price * vals['qty']
        return super().create(vals)