from odoo import models, fields
from odoo.addons import decimal_precision as dp


class MedicalSaleDiscount(models.Model):
    _name = 'medical.sale.discount'
    _description = 'Medical Discounts'

    name = fields.Char(required=True)
    description = fields.Char()
    is_fixed = fields.Boolean(default=False)
    percentage = fields.Float(default=0.0, digits=dp.get_precision('Discount'))
    active = fields.Boolean(default=True)
