# Copyright 2025 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
import re

import pandas as pd
import requests

from odoo import api, fields, models

_logger = logging.getLogger(__name__)
URL_CIMA = "https://cima.aemps.es/cima/rest"


class MedicalCreateFromCimaWizard(models.TransientModel):
    _name = "medical.create.from.cima.wizard"
    _description = "To create a medication from CIMA data"

    name = fields.Char(string="Register Number from CIMA", required=True)

    @api.model
    def create_from_cima(self, nregistro, override=False):
        medicamento = self.env["medical.product.template.commercial"].search(
            [("code", "=", nregistro)], limit=1
        )

        if medicamento and medicamento.product_tmpl_id and not override:
            return medicamento

        df = self._get_presentations_cima(nregistro)
        created_templates = []
        if df.empty:
            return

        for _, row in df.iterrows():
            product_template = self._create_or_get_product_template(
                row, override=override
            )
            created_templates.append(product_template.id)

            product = self._create_or_get_product_product(
                row, product_template, override=override
            )
            template_commercial = self._create_or_get_template_commercial(
                nregistro, row, product_template, override=override
            )
            self._create_or_get_product_commercial(
                row, product, template_commercial, override=override
            )
        return template_commercial

    def _extract_amount(self, dcpf):
        """
        Extract amount and unit of measure from the commercial description (dcpf).
        """
        dcpf = dcpf.lower()
        VALID_UNITS = {
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
        # Seacrh for all pairs of number + word
        matches = re.findall(r"([\.\d]+)\s+([a-záéíóúñ]+)", dcpf)
        for amount, uom in reversed(matches):
            amount = amount.replace(".", "")
            if uom in VALID_UNITS and int(amount) > 0:
                return int(amount), uom.capitalize()

        # Fallback: search for the last number that does not have a dosage unit
        tokens = re.findall(r"(\d+)(?:\s*([a-z/]+))?", dcpf)
        for amount, unit in reversed(tokens):
            if unit and unit.lower() in UOM_DOSIS and int(amount) == 0:
                continue
            return int(amount), "Unidad"
        return 1, "Unidad"

    def _get_or_create_form(self, row):
        form = self.env["medication.form"].search(
            [("api_id", "=", row["forma_farmaceutica_id"])], limit=1
        )

        if not form:
            # Search for 'Unit' category
            uom_category = self.env.ref(
                "uom.product_uom_categ_unit", raise_if_not_found=False
            )
            if not uom_category:
                raise ValueError("Category 'Unit' not found.")

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

    def _create_or_get_product_template(self, row, override=False):
        product_template = self.env["medical.product.template"].search(
            [("code_template", "=", row["dcp_id"])], limit=1
        )

        form = self._get_or_create_form(row)
        routes = self._get_or_create_routes(row)

        if not product_template:
            product_template = self.env["medical.product.template"].create(
                {
                    "name": row["vtm"] or "VTM no disponible",
                    "name_template_cima": row["dcp"],
                    "code_template": row["dcp_id"],
                    "product_type": "medication",
                    "ingredients": row["ingredientes"],
                    "dosage": row["dosages"],
                    "form_id": form.id,
                    "administration_route_ids": [(6, 0, routes.ids)],
                }
            )
        elif override:
            product_template.write(
                {
                    "name": row["vtm"] or "VTM no disponible",
                    "name_template_cima": row["dcp"],
                    "product_type": "medication",
                    "ingredients": row["ingredientes"],
                    "dosage": row["dosages"],
                    "form_id": form.id,
                    "administration_route_ids": [(6, 0, routes.ids)],
                }
            )

        return product_template

    def _create_or_get_product_product(self, row, template, override=False):
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
                    "name_product_cima": row["dcpf"],
                    "product_tmpl_id": template.id,
                    "amount": self._extract_amount(row["dcpf"])[0],
                    "amount_uom_id": uom_id,
                }
            )
        elif override:
            uom_id = (
                template.form_id.uom_ids and template.form_id.uom_ids[0].id or False
            )
            product.write(
                {
                    "code_product": row["dcpf_id"],
                    "name_product_cima": row["dcpf"],
                    "product_tmpl_id": template.id,
                    "amount": self._extract_amount(row["dcpf"])[0],
                    "amount_uom_id": uom_id,
                }
            )

        return product

    def _create_or_get_template_commercial(
        self, nregistro, row, template, override=False
    ):
        commercial = self.env["medical.product.template.commercial"].search(
            [
                ("code", "=", nregistro),
            ],
            limit=1,
        )

        if not commercial:
            commercial = self.env["medical.product.template.commercial"].create(
                {
                    "code": nregistro,
                    "name": row["nombre_medicamento"],
                    "product_tmpl_id": template.id,
                    "laboratory": row["labtitular"],
                    "laboratory_product_name": row["lab_name"],
                    "ft_pdf_link": row["doc_tipo_1"],
                    "prospect_pdf_link": row["doc_tipo_2"],
                    "ipe_pdf_link": row["doc_tipo_3"],
                }
            )
        elif override:
            commercial.write(
                {
                    "code": nregistro,
                    "name": row["nombre_medicamento"],
                    "product_tmpl_id": template.id,
                    "laboratory": row["labtitular"],
                    "laboratory_product_name": row["lab_name"],
                    "ft_pdf_link": row["doc_tipo_1"],
                    "prospect_pdf_link": row["doc_tipo_2"],
                    "ipe_pdf_link": row["doc_tipo_3"],
                }
            )

        return commercial

    def _create_or_get_product_commercial(
        self, row, product, template_commercial, override=False
    ):
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
                    "name_cima": row["nombre_presentacion"],
                    "medical_product_id": product.id,
                    "product_tmpl_commercial_id": template_commercial.id,
                    "active": row.get("active", True),
                }
            )
        elif override:
            commercial.write(
                {
                    "code": row["cn"],
                    "name_cima": row["nombre_presentacion"],
                    "medical_product_id": product.id,
                    "product_tmpl_commercial_id": template_commercial.id,
                    "active": row.get("active", True),
                }
            )
        return commercial

    def doit(self, override=False):
        self.ensure_one()

        template_commercial = self.create_from_cima_data(self.name, override=override)

        return {
            "type": "ir.actions.act_window",
            "name": "New Template Commercial",
            "res_model": "medical.product.template.commercial",
            "view_mode": "form",
            "res_id": template_commercial.id,
            "target": "current",
        }

    def _get_presentations_cima(self, nregistro):
        url_medicamento = f"{URL_CIMA}/medicamento?nregistro={nregistro}"
        response = requests.get(url_medicamento, timeout=30)
        if response.status_code != 200:
            _logger.warning("Code %s not found in CIMA  ", nregistro)
            return pd.DataFrame()

        data = response.json()
        nombre_medicamento = data.get("nombre", "")
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

        # docs
        docs_list = data.get("docs", [])

        doc_tipo_1 = next(
            (doc.get("url") for doc in docs_list if doc.get("tipo") == 1), False
        )
        doc_tipo_2 = next(
            (doc.get("url") for doc in docs_list if doc.get("tipo") == 2), False
        )
        doc_tipo_3 = next(
            (doc.get("url") for doc in docs_list if doc.get("tipo") == 3), False
        )

        labtitular = data.get("labtitular", "")
        lab_name = data.get("nombre", "")

        resultados = []
        for presentacion in data.get("presentaciones", []):
            cn = presentacion.get("cn")
            url_pres = f"{URL_CIMA}/presentaciones?cn={cn}"
            resp_pres = requests.get(url_pres, timeout=30)
            if resp_pres.status_code != 200:
                continue
            pres_data = resp_pres.json().get("resultados", [])
            if not pres_data:
                continue

            detalle = pres_data[0]
            resultados.append(
                {
                    "n_registro": nregistro,
                    "nombre_medicamento": nombre_medicamento,
                    "cn": detalle.get("cn"),
                    "nombre_presentacion": detalle.get("nombre"),
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
                    "doc_tipo_1": doc_tipo_1,
                    "doc_tipo_2": doc_tipo_2,
                    "doc_tipo_3": doc_tipo_3,
                    "active": detalle.get("comerc", True),
                }
            )

        return pd.DataFrame(resultados)
