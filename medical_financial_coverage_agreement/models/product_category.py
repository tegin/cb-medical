# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductCategory(models.Model):

    _inherit = 'product.category'

    level = fields.Integer(compute='_compute_tree_level', store=True)
    description = fields.Char()

    @api.depends('parent_id')
    def _compute_tree_level(self):
        for record in self:
            if not record.parent_id:
                record.level = 0
            else:
                record.level = record.parent_id.level + 1
