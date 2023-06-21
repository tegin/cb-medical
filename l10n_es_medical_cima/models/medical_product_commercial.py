# Copyright 2022 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
import re

from odoo import api, fields, models

from ..fields import UnaccentedChar


class MedicalProductTemplateCommercial(models.Model):

    _name = "medical.product.template.commercial"
    _description = "Medical Product Template Commercial"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(compute="_compute_name")

    product_tmpl_id = fields.Many2one("medical.product.template")

    product_tmpl_name = fields.Char(related="product_tmpl_id.name_template")

    code = fields.Char(string="Registration Code")

    laboratory = fields.Char()

    laboratory_product_name = fields.Char()
    unaccented_laboratory_product_name = UnaccentedChar(
        related="laboratory_product_name",
        store=True,
        index=True,
        string="Unnacented name",
    )

    product_ids = fields.One2many(
        "medical.product.product.commercial",
        inverse_name="product_tmpl_commercial_id",
    )
    active = fields.Boolean(compute="_compute_active", store=True)
    product_count = fields.Integer(compute="_compute_commercial_product_ids")
    technical_doc = fields.Char()
    leafleft_doc = fields.Char()
    technical_html = fields.Char()
    leafleft_html = fields.Char()
    generic = fields.Boolean()
    prescription = fields.Boolean()
    in_patient = fields.Boolean()
    narcotic = fields.Boolean()
    long_term_treatment = fields.Boolean()
    psychotropic = fields.Boolean()

    @api.depends("product_ids.active")
    def _compute_active(self):
        for record in self:
            record.active = any(record.product_ids.mapped("active"))

    @api.depends("product_ids")
    def _compute_commercial_product_ids(self):
        for rec in self:
            rec.product_count = len(rec.product_ids)

    def _get_name_fields(self):
        return ["product_tmpl_name", "laboratory"]

    @api.depends(_get_name_fields)
    def _compute_name(self):
        for rec in self:
            name = ""
            for field in rec._get_name_fields():
                if getattr(rec, field):
                    name += " %s" % getattr(rec, field)
            rec.name = name

    def action_view_medical_product_commercial_ids(self):
        action = self.env.ref(
            "l10n_es_medical_cima.medical_product_product_commercial_act_window"
        ).read()[0]
        action["domain"] = [("product_tmpl_commercial_id", "=", self.id)]
        if len(self.product_ids) == 1:
            view = (
                "l10n_es_medical_cima." "medical_product_product_commercial_form_view"
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
    unaccented_code = UnaccentedChar(
        related="code", store=True, index=True, string="Unnacented code"
    )

    medical_product_id = fields.Many2one("medical.product.product")

    medical_product_name = fields.Char(related="medical_product_id.name_product")

    product_tmpl_id = fields.Many2one(
        "medical.product.template",
        related="medical_product_id.product_tmpl_id",
        store=True,
    )

    product_tmpl_commercial_domain = fields.Char(
        compute="_compute_product_tmpl_commercial_domain"
    )
    product_tmpl_commercial_id = fields.Many2one("medical.product.template.commercial")

    laboratory = fields.Char(related="product_tmpl_commercial_id.laboratory")
    laboratory_product_name = fields.Char(
        related="product_tmpl_commercial_id.laboratory_product_name"
    )
    active = fields.Boolean(default=True)
    in_patient = fields.Boolean()

    _sql_constraints = [
        ("code_uniq", "UNIQUE(code)", "Code must be unique!"),
    ]

    def _import_cima_data(self, presentation_data, product_data):
        product_tmpl = self._get_medical_product_tmpl(presentation_data, product_data)
        commercial_product_tmpl = self._get_medical_product_tmpl_commercial(
            product_tmpl, presentation_data, product_data
        )
        product = self._get_medical_product(
            product_tmpl, presentation_data, product_data
        )
        return self._get_medical_product_commercial(
            product_tmpl,
            commercial_product_tmpl,
            product,
            presentation_data,
            product_data,
        )

    def _get_medical_product_tmpl(self, presentation_data, product_data):
        product_tmpl = self.env["medical.product.template"].search(
            [("cima_ref", "=", presentation_data["dcp"]["id"])]
        )
        vals = self._get_medical_product_tmpl_vals(presentation_data, product_data)
        if product_tmpl:
            product_tmpl.write(vals)
        else:
            product_tmpl = product_tmpl.create(vals)
        return product_tmpl

    def _get_medical_product_tmpl_vals(self, presentation_data, product_data):
        return {
            "cima_ref": presentation_data["dcp"]["id"],
            "name": presentation_data["dcp"]["nombre"],
            "code_template": presentation_data["dcp"]["id"],
            "ingredients": ", ".join(
                [
                    ingredient.get("nombre", "")
                    for ingredient in product_data.get("principiosActivos", [])
                ]
            ),
            "dosage": product_data.get("dosis"),
            "form_id": self._get_form_cima(presentation_data, product_data).id,
            "administration_route_ids": [
                (
                    6,
                    0,
                    self._get_administration_route_cima(
                        presentation_data, product_data
                    ).ids,
                )
            ],
            "can_drive": not product_data["conduc"],
        }

    def _get_form_cima(self, presentation_data, product_data):
        form = self.env["medication.form"].search(
            [
                (
                    "cima_ref",
                    "=",
                    str(product_data["formaFarmaceuticaSimplificada"]["id"]),
                )
            ]
        )
        if form:
            return form
        return form.create(self._get_form_cima_vals(presentation_data, product_data))

    def _get_form_cima_vals(self, presentation_data, product_data):
        return {
            "cima_ref": str(product_data["formaFarmaceuticaSimplificada"]["id"]),
            "name": product_data["formaFarmaceuticaSimplificada"]["nombre"],
            "uom_ids": [(6, 0, self.env.ref("uom.product_uom_unit").ids)],
        }

    def _get_administration_route_cima(self, presentation_data, product_data):
        routes = self.env["medical.administration.route"]
        for route_vals in product_data.get("viasAdministracion", []):
            route = self.env["medical.administration.route"].search(
                [("cima_ref", "=", str(route_vals["id"]))]
            )
            if not route:
                route = route.create(
                    {"cima_ref": str(route_vals["id"]), "name": route_vals["nombre"]}
                )
            routes |= route
        return routes

    def _get_medical_product_tmpl_commercial(
        self, product_tmpl, presentation_data, product_data
    ):
        product = self.env["medical.product.template.commercial"].search(
            [("code", "=", presentation_data["nregistro"])]
        )
        vals = self._get_medical_product_tmpl_commercial_vals(
            product_tmpl, presentation_data, product_data
        )
        if product:
            product.write(vals)
        else:
            product = product.create(vals)
        return product

    def _get_medical_product_tmpl_commercial_vals(
        self, product_tmpl, presentation_data, product_data
    ):
        prescription_info = {d.strip() for d in product_data["cpresc"].split(".")}
        vals = {
            "code": presentation_data["nregistro"],
            "product_tmpl_id": product_tmpl.id,
            "laboratory": presentation_data["labtitular"],
            "laboratory_product_name": product_data["nombre"],
            "generic": product_data.get("generico"),
            "prescription": product_data.get("receta"),
            "in_patient": bool(
                {
                    "Uso Hospitalario",
                    "Diagnóstico Hospitalario",
                    "Uso Hospitalario Y Centros De Diagnóstico Autorizados",
                }
                & prescription_info
            ),
            "narcotic": bool({"Estupefacientes"} & prescription_info),
            "long_term_treatment": bool(
                {"Tratamiento De Larga Duración"} & prescription_info
            ),
            "psychotropic": bool({"Psicótropos"} & prescription_info),
        }
        for doc in product_data["docs"]:
            if doc["tipo"] == "1":
                vals["technical_doc"] = doc["url"]
                if "urlHtml" in doc:
                    vals["technical_html"] = doc["urlHtml"]
            if doc["tipo"] == "2":
                vals["leafleft_doc"] = doc["url"]
                if "urlHtml" in doc:
                    vals["leafleft_html"] = doc["urlHtml"]

        return vals

    def _get_medical_product(self, product_tmpl, presentation_data, product_data):
        product = self.env["medical.product.product"].search(
            [("cima_ref", "=", presentation_data["dcpf"]["id"])]
        )
        if not product:
            vals = self._get_medical_product_vals(
                product_tmpl, presentation_data, product_data
            )
            product = product.create(vals)
        elif not self.env.context.get("no_update_cima_data"):
            vals = self._get_medical_product_vals(
                product_tmpl, presentation_data, product_data
            )
            product.write(vals)
        return product

    def _get_medical_product_vals(self, product_tmpl, presentation_data, product_data):
        match = re.match(
            product_data["nombre"].replace("\\", "\\\\")
            + r"\s*,?\s*(?P<units>\d*,?\d+)",
            presentation_data["nombre"],
        )
        vals = {
            "cima_ref": presentation_data["dcpf"]["id"],
            "name": presentation_data["dcpf"]["nombre"],
            "product_tmpl_id": product_tmpl.id,
            "code_product": presentation_data["dcpf"]["id"],
            "amount_uom_id": self.env.ref("uom.product_uom_unit").id,
        }
        if match is not None:
            vals["amount"] = float(match.groupdict()["units"].replace(",", "."))
        return vals

    def _get_medical_product_commercial(
        self,
        product_tmpl,
        commercial_product_tmpl,
        product,
        presentation_data,
        product_data,
    ):
        product_commercial = self.search([("code", "=", presentation_data["cn"])])
        vals = self._get_medical_product_commercial_vals(
            product_tmpl,
            commercial_product_tmpl,
            product,
            presentation_data,
            product_data,
        )
        if product_commercial:
            product_commercial.write(vals)
        else:
            product_commercial = self.create(vals)
        return product_commercial

    def _get_medical_product_commercial_vals(
        self,
        product_tmpl,
        commercial_product_tmpl,
        product,
        presentation_data,
        product_data,
    ):
        prescription_info = {d.strip() for d in presentation_data["cpresc"].split(".")}
        return {
            "code": presentation_data["cn"],
            "name": presentation_data["nombre"],
            "medical_product_id": product.id,
            "product_tmpl_commercial_id": commercial_product_tmpl.id,
            "active": presentation_data["comerc"],
            "in_patient": bool(
                {
                    "Uso Hospitalario",
                    "Diagnóstico Hospitalario",
                    "Uso Hospitalario Y Centros De Diagnóstico Autorizados",
                }
                & prescription_info
            ),
        }

    @api.depends("medical_product_id")
    def _compute_product_tmpl_commercial_domain(self):
        for rec in self:
            if rec.medical_product_id:
                domain = json.dumps(
                    [
                        (
                            "product_tmpl_id",
                            "=",
                            rec.medical_product_id.product_tmpl_id.id,
                        )
                    ]
                )
            else:
                domain = json.dumps([("product_tmpl_id", "=", 0)])
            rec.product_tmpl_commercial_domain = domain

    def _get_name_fields(self):
        return ["code", "medical_product_name", "laboratory"]

    @api.depends(_get_name_fields)
    def _compute_name(self):
        for rec in self:
            name = ""
            for field in rec._get_name_fields():
                if getattr(rec, field):
                    name += " %s" % getattr(rec, field)
            rec.name = name
