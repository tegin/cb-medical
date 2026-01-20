# Copyright 2022 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class MedicalProductTemplateCommercial(models.Model):

    _name = "medical.product.template.commercial"
    _description = "Medical Product Template Commercial"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "name"

    name = fields.Char(compute="_compute_name", store=True, readonly=False)

    product_tmpl_id = fields.Many2one("medical.product.template")

    product_tmpl_name = fields.Char(related="product_tmpl_id.name_template")

    code = fields.Char(string="Registration Code")

    laboratory = fields.Char()

    laboratory_product_name = fields.Char()

    product_ids = fields.One2many(
        "medical.product.product.commercial",
        inverse_name="product_tmpl_commercial_id",
    )

    product_count = fields.Integer(compute="_compute_commercial_product_ids")

    @api.depends("product_ids")
    def _compute_commercial_product_ids(self):
        for rec in self:
            rec.product_count = len(rec.product_ids)

    def _get_name_fields(self):
        return ["product_tmpl_id.name", "laboratory"]

    @api.depends(lambda self: self._get_name_fields())
    def _compute_name(self):
        for rec in self:
            rec.name = rec._get_name()

    def _get_name(self):
        name = []
        for field in self._get_name_fields():
            value = self.mapped(field)[0]
            if value:
                name.append(value)
        return " ".join(name)

    def action_view_medical_product_commercial_ids(self):
        action = self.env.ref(
            "cb_medical_product_request.medical_product_product_commercial_act_window"
        ).read()[0]
        action["domain"] = [("product_tmpl_commercial_id", "=", self.id)]
        if len(self.product_ids) == 1:
            view = (
                "cb_medical_product_request."
                "medical_product_product_commercial_form_view"
            )
            form_view = [(self.env.ref(view).id, "form")]
            if "views" in action:
                action["views"] = form_view + [
                    (state, view) for state, view in action["views"] if view != "form"
                ]
            else:
                action["views"] = form_view
            action["res_id"] = self.product_ids.id
        return action


class MedicalProductProductCommercial(models.Model):

    _name = "medical.product.product.commercial"
    _description = "Medical Product Product Commercial"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(compute="_compute_name")

    code = fields.Char(string="National Code")

    medical_product_id = fields.Many2one("medical.product.product")

    medical_product_name = fields.Char(related="medical_product_id.name_product")

    product_tmpl_id = fields.Many2one(
        "medical.product.template",
        related="medical_product_id.product_tmpl_id",
        store=True,
    )
    product_tmpl_commercial_id = fields.Many2one("medical.product.template.commercial")

    laboratory_product_name = fields.Char(
        related="product_tmpl_commercial_id.laboratory_product_name"
    )

    def _get_name_fields(self):
        return [
            "code",
            "medical_product_id.name_product",
            "product_tmpl_commercial_id.laboratory",
        ]

    @api.depends(lambda self: self._get_name_fields())
    def _compute_name(self):
        for rec in self:
            rec.name = rec._get_name()

    def _get_name(self):
        name = []
        for field in self._get_name_fields():
            value = self.mapped(field)[0]
            if value:
                name.append(value)
        return " ".join(name)
