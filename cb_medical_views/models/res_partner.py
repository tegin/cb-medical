from odoo import models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def name_get(self):
        orig = super().name_get()
        if not self.env.context.get("cb_display", False):
            return orig
        orig_name = dict(orig)
        result = []
        for partner in self:
            name = orig_name[partner.id]
            if partner.is_payor:
                name = partner.comercial or name
            result.append((partner.id, name))
        return result
