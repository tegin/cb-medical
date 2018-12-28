from odoo import fields, models


class MedicalQuoteLayoutCategory(models.Model):
    _name = 'medical.quote.layout_category'
    _description = 'Medical Quote Layout Category'
    _order = 'sequence, id'

    name = fields.Char('Name', required=True, translate=True)
    sequence = fields.Integer('Sequence', required=True, default=10)
    subtotal = fields.Boolean('Add subtotal', default=True)
    pagebreak = fields.Boolean('Add pagebreak')
    quote_id = fields.Many2one('medical.quote', string='Quote',
                               ondelete='cascade')
