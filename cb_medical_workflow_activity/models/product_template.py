from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    activity_tmpl_definition_ids = fields.One2many(
        "workflow.activity.definition",
        inverse_name="service_tmpl_id",
        readonly=True,
    )

    def get_tmpl_activity(self):
        return self.product_variant_id.get_activity()

    def generate_tmpl_activity(self):
        return self.product_variant_id.generate_activity()

    @api.constrains("type")
    def _check_activities(self):
        for rec in self:
            if rec.type != "service" and rec.activity_tmpl_definition_ids:
                raise ValidationError(_("Activities are only allowed for services"))
