# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64

import requests
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class WizardCreateMedication(models.TransientModel):

    _name = "wizard.create.medication"
    _description = "wizard.create.medication"

    register_number = fields.Char(required=True)

    def get_vals_from_doc(self, docs, product):
        vals = []
        for doc in docs:
            fname = doc["url"].split("/")[-1]
            response = requests.get(doc["url"])
            response.raise_for_status()
            vals.append(
                {
                    "name": fname,
                    "datas": base64.b64encode(response.content),
                    "datas_fname": fname,
                    "mimetype": "application/pdf",
                    "res_model": "product.product",
                    "res_id": product.id,
                }
            )
        return vals

    @api.multi
    def create_medication(self):
        if self.env["product.product"].search(
            [("register_number", "=", self.register_number)], limit=1
        ):
            raise ValidationError(_("This medication is already imported"))
        r = requests.get(
            url="https://cima.aemps.es/cima/rest/medicamento",
            params={"nregistro": self.register_number},
        )
        r.raise_for_status()
        if r.status_code == 204:
            raise ValidationError(_("Register Number not found."))
        data = r.json()

        atc_code_5 = False
        template_name = False
        for atc in data["atcs"]:
            if atc["nivel"] == 5:
                atc_code_5 = atc["codigo"]
                template_name = atc["nombre"]
                break
        if not atc_code_5:
            raise ValidationError(
                _("This medication does not have a level 5 ATC Code")
            )

        template = self.env["product.template"].search(
            [("atc_code_5", "=", atc_code_5)], limit=1
        )

        if not template:
            template = (
                self.env["product.template"]
                .with_context(create_product_product=False)
                .create({"name": template_name, "atc_code_5": atc_code_5})
            )

        # Get image
        image = False
        for photo in data.get("fotos", []):
            if photo["tipo"] == "materialas":
                response = requests.get(photo["url"])
                response.raise_for_status()
                image = base64.b64encode(response.content)
                break

        # Add PDFs
        pdfs = {}
        for doc in data.get("docs", []):
            if doc["tipo"] < 3:
                response = requests.get(doc["url"])
                response.raise_for_status()
                pdfs[doc["tipo"]] = base64.b64encode(response.content)

        product = self.env["product.product"].create(
            {
                "medication_name": data["nombre"],
                "product_tmpl_id": template.id,
                "register_number": self.register_number,
                "is_medication": True,
                "over_the_counter": data["receta"],
                "psum": data["psum"],
                "image_medium": image,
                "data_sheet": pdfs.get(1, False),
                "leaflet": pdfs.get(2, False),
            }
        )

        action = {
            "type": "ir.actions.act_window",
            "name": product.name,
            "res_model": "product.product",
            "res_id": product.id,
            "view_mode": "form",
            "view_type": "form",
            "views": [
                (
                    self.env.ref("product.product_variant_easy_edit_view").id,
                    "form",
                )
            ],
        }
        return action
