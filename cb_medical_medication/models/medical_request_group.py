from odoo import _, models


class MedicalRequestGroup(models.Model):
    _inherit = "medical.request.group"

    def get_sale_order_line_vals(self, is_insurance):
        res = super().get_sale_order_line_vals(is_insurance)
        if self.child_model == "medical.medication.request":
            request = self.env[self.child_model].browse(self.child_id)
            if request.location_type_id:
                res["name"] = _("{} on {}").format(
                    res["name"], request.location_type_id.name,
                )
        return res
