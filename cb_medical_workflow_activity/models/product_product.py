from odoo import _, fields, models
from odoo.exceptions import ValidationError


class ProductProduct(models.Model):
    _inherit = "product.product"

    activity_definition_ids = fields.One2many(
        "workflow.activity.definition",
        inverse_name="service_id",
        readonly=True,
    )

    def _get_activity_vals(self):
        model = self.env.ref(
            "medical_clinical_procedure.model_medical_procedure_request"
        )
        return {
            "name": self.name,
            "model_id": model.id,
            "service_id": self.id,
            "service_tmpl_id": self.product_tmpl_id.id,
        }

    def get_activity(self):
        result = self.env["ir.actions.act_window"]._for_xml_id(
            "medical_workflow.workflow_activity_definition_action"
        )
        result["domain"] = [("service_id", "=", self.id)]
        if len(self.activity_definition_ids) == 1:
            result["views"] = [(False, "form")]
            result["res_id"] = self.activity_definition_ids.id
        return result

    def _generate_activity(self):
        if self.activity_definition_ids:
            return self.activity_definition_ids
        if self.type != "service":
            raise ValidationError(_("Activities are only allowed for services"))
        activity = self.env["workflow.activity.definition"].create(
            self._get_activity_vals()
        )
        activity.activate()
        return activity

    def generate_activity(self):
        self._generate_activity()
        return self.get_activity()
