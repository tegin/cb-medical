# Copyright 2025 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
import re

import pandas as pd
import requests

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class MedicalCreateFromCimaWizard(models.TransientModel):
    _name = "medical.create.from.cima.wizard"
    _description = "Crear medicamento desde CIMA"

    name = fields.Char(string="Nº de Registro CIMA", required=True)

    @api.model
    def create_from_cima(self, nregistro):
        wizard = self.env["medical.create.from.cima.wizard"].create({"name": nregistro})
        return wizard.doit()

    def _extraer_amount(self, dcpf):
        """
        Extrae cantidad y unidad de medida desde la descripción comercial.
        Prioriza pares número + palabra relevantes (comprimidos, sobres, etc).
        """
        dcpf = dcpf.lower()
        UNIDADES_VALIDAS = {
            "comprimidos",
            "sobres",
            "cápsulas",
            "jeringas",
            "ampollas",
            "viales",
            "frascos",
            "envases",
            "tabletas",
            "blísters",
            "frasco",
            "bolsas",
        }
        UOM_DOSIS = {"mg", "ml", "g", "mcg", "μg", "ppm", "l"}
        # Buscar todos los pares número + palabra
        matches = re.findall(r"(\d+)\s+([a-záéíóúñ]+)", dcpf)

        for amount, uom in reversed(matches):
            if uom in UNIDADES_VALIDAS:
                return int(amount), uom.capitalize()

        # 2. Fallback: buscar el último número que NO vaya con una unidad de dosis
        tokens = re.findall(r"(\d+)(?:\s*([a-z/]+))?", dcpf)
        for amount, unit in reversed(tokens):
            if unit and unit.lower() in UOM_DOSIS:
                continue
            return int(amount), "Unidad"
        return 1, "Unidad"

    def _get_or_create_form(self, row):
        form = self.env["medication.form"].search(
            [("api_id", "=", row["forma_farmaceutica_id"])], limit=1
        )

        if not form:
            # Buscar categoría 'Unit'
            uom_category = self.env.ref(
                "uom.product_uom_categ_unit", raise_if_not_found=False
            )
            if not uom_category:
                raise ValueError("Categoría 'Unit' no encontrada.")

            unit_uom = self.env["uom.uom"].search(
                [
                    ("name", "=", row["forma_farmaceutica_simplificada"]),
                    ("category_id", "=", uom_category.id),
                ],
                limit=1,
            )

            if not unit_uom:
                unit_uom = self.env["uom.uom"].create(
                    {
                        "name": row["forma_farmaceutica_simplificada"],
                        "category_id": uom_category.id,
                        "uom_type": "bigger",
                        "factor": 1.0,
                    }
                )

            form = self.env["medication.form"].create(
                {
                    "name": row["forma_farmaceutica"],
                    "api_id": row["forma_farmaceutica_id"],
                    "uom_ids": [(6, 0, [unit_uom.id])],
                }
            )

        return form

    def _get_or_create_routes(self, row):
        routes = self.env["medical.administration.route"].search(
            [("api_id", "in", row["vias_administracion_ids"].split(", "))]
        )

        if not routes:
            routes = self.env["medical.administration.route"].create(
                [
                    {"name": name.strip(), "api_id": api_id.strip()}
                    for api_id, name in zip(
                        row["vias_administracion_ids"].split(", "),
                        row["vias_administracion_nombres"].split(", "),
                    )
                ]
            )
        return routes

    def _create_or_get_product_template(self, row):
        product_template = self.env["medical.product.template"].search(
            [("code_template", "=", row["dcp_id"])], limit=1
        )

        form = self._get_or_create_form(row)
        routes = self._get_or_create_routes(row)

        if not product_template:
            product_template = self.env["medical.product.template"].create(
                {
                    "name": row["vtm"],
                    "code_template": row["dcp_id"],
                    "product_type": "medication",
                    "ingredients": row["ingredientes"],
                    "dosage": row["dosages"],
                    "form_id": form.id,
                    "administration_route_ids": [(6, 0, routes.ids)],
                }
            )

        return product_template

    def _create_or_get_product_product(self, row, template):
        product = self.env["medical.product.product"].search(
            [
                ("code_product", "=", row["dcpf_id"]),
            ],
            limit=1,
        )

        if not product:
            uom_id = (
                template.form_id.uom_ids and template.form_id.uom_ids[0].id or False
            )
            product = self.env["medical.product.product"].create(
                {
                    "code_product": row["dcpf_id"],
                    "product_tmpl_id": template.id,
                    "amount": self._extraer_amount(row["dcpf"])[0],
                    "amount_uom_id": uom_id,
                }
            )

        return product

    def _create_or_get_template_commercial(self, row, template):
        commercial = self.env["medical.product.template.commercial"].search(
            [
                ("code", "=", self.name),
            ],
            limit=1,
        )

        if not commercial:
            commercial = self.env["medical.product.template.commercial"].create(
                {
                    "code": self.name,
                    "product_tmpl_id": template.id,
                    "laboratory": row["labtitular"],
                    "laboratory_product_name": row["lab_name"],
                }
            )

        return commercial

    def _create_or_get_product_commercial(self, row, product, template_commercial):
        commercial = self.env["medical.product.product.commercial"].search(
            [
                ("code", "=", row["cn"]),
            ],
            limit=1,
        )

        if not commercial:
            commercial = self.env["medical.product.product.commercial"].create(
                {
                    "code": row["cn"],
                    "medical_product_id": product.id,
                    "product_tmpl_commercial_id": template_commercial.id,
                }
            )

        return commercial

    def doit(self):
        self.ensure_one()

        medicamento = self.env["medical.product.template.commercial"].search(
            [("code", "=", self.name)], limit=1
        )

        if medicamento and medicamento.product_tmpl_id:
            return {
                "type": "ir.actions.act_window",
                "name": "Medicamento Existente",
                "res_model": "medical.product.template.commercial",
                "view_mode": "form",
                "res_id": medicamento.id,
                "target": "current",
            }

        df = self._obtener_presentaciones_cima(self.name)
        created_templates = []
        if df.empty:
            return

        for _, row in df.iterrows():
            product_template = self._create_or_get_product_template(row)
            created_templates.append(product_template.id)

            product = self._create_or_get_product_product(row, product_template)
            template_commercial = self._create_or_get_template_commercial(
                row, product_template
            )
            self._create_or_get_product_commercial(row, product, template_commercial)

        return {
            "type": "ir.actions.act_window",
            "name": "Nuevo Template Comercial",
            "res_model": "medical.product.template.commercial",
            "view_mode": "form",
            "res_id": template_commercial.id,
            "target": "current",
        }

    def _obtener_presentaciones_cima(self, nregistro):
        url_medicamento = (
            f"https://cima.aemps.es/cima/rest/medicamento?nregistro={nregistro}"
        )
        response = requests.get(url_medicamento, timeout=10)
        if response.status_code != 200:
            _logger.warning(
                "Medicamento no encontrado en CIMA para nregistro %s", nregistro
            )
            return pd.DataFrame()  # Devuelve vacío y el método `doit()` lo ignora

        data = response.json()
        forma_farmaceutica_id = data.get("formaFarmaceutica", {}).get("id")
        forma_farmaceutica = data.get("formaFarmaceutica", {}).get("nombre")

        forma_farmaceutica_simplificada_id = data.get(
            "formaFarmaceuticaSimplificada", {}
        ).get("id")
        forma_farmaceutica_simplificada = data.get(
            "formaFarmaceuticaSimplificada", {}
        ).get("nombre")

        vias = data.get("viasAdministracion", [])
        vias_ids = ", ".join(str(v.get("id")) for v in vias)
        vias_nombres = ", ".join(v.get("nombre") for v in vias)

        principios = data.get("principiosActivos", [])
        ingredientes = ", ".join(p.get("nombre") for p in principios)
        dosages = ", ".join(
            p.get("cantidad") + " " + p.get("unidad") for p in principios
        )

        # laboratorio titular
        labtitular = data.get("labtitular", "")
        lab_name = data.get("nombre", "")

        resultados = []
        for presentacion in data.get("presentaciones", []):
            cn = presentacion.get("cn")
            url_pres = f"https://cima.aemps.es/cima/rest/presentaciones?cn={cn}"
            resp_pres = requests.get(url_pres, timeout=10)
            if resp_pres.status_code != 200:
                continue
            pres_data = resp_pres.json().get("resultados", [])
            if not pres_data:
                continue

            detalle = pres_data[0]
            resultados.append(
                {
                    "n_registro": nregistro,
                    "cn": detalle.get("cn"),
                    "vtm_id": detalle.get("vtm", {}).get("id"),
                    "vtm": detalle.get("vtm", {}).get("nombre"),
                    "dcp_id": detalle.get("dcp", {}).get("id") or "DCP no disponible",
                    "dcp": detalle.get("dcp", {}).get("nombre") or "DCP no disponible",
                    "dcpf_id": detalle.get("dcpf", {}).get("id")
                    or "DCPF no disponible",
                    "dcpf": detalle.get("dcpf", {}).get("nombre")
                    or "DCPF no disponible",
                    "forma_farmaceutica_simplificada_id": forma_farmaceutica_simplificada_id,
                    "forma_farmaceutica_simplificada": forma_farmaceutica_simplificada,
                    "forma_farmaceutica_id": forma_farmaceutica_id,
                    "forma_farmaceutica": forma_farmaceutica,
                    "vias_administracion_ids": vias_ids,
                    "vias_administracion_nombres": vias_nombres,
                    "ingredientes": ingredientes,
                    "dosages": dosages,
                    "labtitular": labtitular,
                    "lab_name": lab_name,
                }
            )

        return pd.DataFrame(resultados)
