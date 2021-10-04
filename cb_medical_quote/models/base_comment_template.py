from odoo import models


class BaseCommentTemplate(models.Model):

    _inherit = "base.comment.template"

    def get_value(self, partner_id=False):
        self.ensure_one()
        lang = None
        if partner_id:
            lang = self.env["res.partner"].browse(partner_id).lang
        return self.with_context({"lang": lang}).text
