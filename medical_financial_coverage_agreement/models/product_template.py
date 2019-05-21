# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    include_zero_sales = fields.Boolean(
        default=False
    )

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        if 'categ_id' in vals:
            self.env['medical.coverage.agreement.item'].search([
                ('product_id', 'in', self.mapped('product_variant_ids').ids)
            ]).write({'categ_id': vals['categ_id']})
        return res


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        if 'categ_id' in vals:
            self.env['medical.coverage.agreement.item'].search([
                ('product_id', 'in', self.ids)
            ]).write({'categ_id': vals['categ_id']})
        return res
