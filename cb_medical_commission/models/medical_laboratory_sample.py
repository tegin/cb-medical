from odoo import models


class MedicalLaboratoryRequest(models.Model):
    _inherit = "medical.laboratory.sample"

    def _get_event_values(self, vals=False):
        res = super()._get_event_values(vals=vals)
        conditions = self.performer_id.practitioner_condition_ids
        practitioner_condition_id = conditions.get_condition(
            self.request_group_id.service_id, self.service_id, self.center_id
        )
        if practitioner_condition_id:
            res.update({"practitioner_condition_id": practitioner_condition_id.id})
        return res

    def generate_event(self, vals=False):
        res = super().generate_event(vals=vals)
        for r in res:
            r.compute_commission()
        return res
