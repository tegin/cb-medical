from odoo import api, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def _name_search(
        self,
        name="",
        args=None,
        operator="ilike",
        limit=100,
        name_get_uid=None,
    ):
        res = super()._name_search(
            name=name,
            args=args,
            operator=operator,
            limit=limit,
            name_get_uid=name_get_uid,
        )
        if not res and self.env.context.get("search_on_supplier"):
            suppliers = self.env["product.supplierinfo"].search(
                [
                    "|",
                    ("product_code", operator, name),
                    ("product_name", operator, name),
                ]
            )
            if suppliers:
                return self.search(
                    [("product_tmpl_id.seller_ids", "in", suppliers.ids)],
                    limit=limit,
                ).name_get()
        return res
