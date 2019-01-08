from odoo import api, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def name_get(self):
        orig_name = dict(super().name_get())
        if not self.env.context.get('cb_display', False):
            return orig_name
        result = []
        for partner in self:
            name = orig_name[partner.id]
            if partner.is_payor:
                name = partner.comercial or name
            result.append((partner.id, name))
        return result
