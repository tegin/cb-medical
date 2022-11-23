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
        workflow = self.env.ref("medical_workflow.medical_workflow")
        model = self.env.ref(
            "medical_clinical_procedure.model_medical_procedure_request"
        )
        return {
            "type_id": workflow.id,
            "name": self.name,
            "model_id": model.id,
            "service_id": self.id,
            "service_tmpl_id": self.product_tmpl_id.id,
        }

    def get_activity(self):
        action = self.env.ref("medical_workflow.workflow_activity_definition_action")
        result = action.read()[0]
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
