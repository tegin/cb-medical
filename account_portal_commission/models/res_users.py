from odoo import _, models


class ResUsers(models.Model):
    _inherit = "res.users"

    def action_open_wizard(self):
        w = self.env["search_encounters.wizard"].create({})
        return {
            "type": "ir.actions.act_window",
            "target": "new",
            "res_model": "search_encounters.wizard",
            "name": _("Search Encounters"),
            "res_id": w.id,
            "views": [(False, "form")],
            "context": self.env.context,
        }
