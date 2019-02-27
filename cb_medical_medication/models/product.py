from odoo import api, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        res = super().name_search(
            name=name, args=args, operator=operator, limit=limit)
        if not res and self.env.context.get('search_on_supplier'):
            suppliers = self.env['product.supplierinfo'].search([
                '|',
                ('product_code', operator, name),
                ('product_name', operator, name)
            ])
            if suppliers:
                return self.search(
                    [('product_tmpl_id.seller_ids', 'in', suppliers.ids)],
                    limit=limit).name_get()
        return res
