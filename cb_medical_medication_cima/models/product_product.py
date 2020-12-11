# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
from collections import defaultdict
from datetime import timedelta

import requests
from odoo import _, api, fields, models


class ProductProduct(models.Model):

    _inherit = "product.product"

    register_number = fields.Char()

    medication_name = fields.Char()
    computed_name = fields.Char(compute="_compute_computed_name")

    psum = fields.Boolean(string="Supply Problem")

    data_sheet = fields.Binary(attachment=True)
    leaflet = fields.Binary(attachment=True)

    # TODO: Missing ATC.

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        # Make a search with default criteria
        names1 = super().name_search(
            name=name, args=args, operator=operator, limit=limit
        )
        # Make the other search
        names2 = []
        if name:
            domain = [("product_tmpl_id.name", "=ilike", name + "%")]
            names2 = self.search(domain, limit=limit).name_get()
        # Merge both results
        return list(set(names1) | set(names2))[:limit]

    @api.depends("name", "medication_name", "is_medication")
    def _compute_computed_name(self):
        for record in self:
            record.computed_name = (
                record.medication_name if record.is_medication else record.name
            )

    def process_medication_changes(self, results):
        joined_changes = defaultdict(set)
        for result in results:
            joined_changes[result["nregistro"]] = joined_changes[
                result["nregistro"]
            ].union(set(result["cambio"]))
        channel = self.env.ref(
            "cb_medical_medication_cima.channel_notify_psum"
        )
        psum_value = False
        for key in joined_changes.keys():
            values_to_write = {}
            try:
                r = requests.get(
                    url="https://cima.aemps.es/cima/rest/medicamento",
                    params={"nregistro": key},
                )
                r.raise_for_status()
                data = r.json()
            except requests.exceptions.HTTPError:
                continue
            for field in joined_changes[key]:
                if field == "ft":
                    for doc in data["docs"]:
                        if doc["tipo"] == 1:
                            response = requests.get(doc["url"])
                            response.raise_for_status()
                            values_to_write["data_sheet"] = base64.b64encode(
                                response.content
                            )
                            break

                if field == "prosp":
                    for doc in data["docs"]:
                        if doc["tipo"] == 2:
                            response = requests.get(doc["url"])
                            response.raise_for_status()
                            values_to_write["leaflet"] = base64.b64encode(
                                response.content
                            )
                            break

                if field == "psum":
                    psum_value = data["psum"]
            product = self.search(
                [("register_number", "=", str(key))], limit=1
            )

            if product and product.psum != psum_value:
                body_message = (
                    _("%s has supply problems!")
                    if psum_value
                    else _("%s no longer has supply problems!")
                )
                product.message_post(
                    body=body_message % product.medication_name,
                    message_type="notification",
                    subtype="mail.mt_comment",
                    channel_ids=[(4, channel.id)],
                )
                values_to_write["psum"] = psum_value
            product.write(values_to_write)

    @api.model
    def _cron_check_medication_changes(
        self, register_numbers=False, date=False
    ):
        if not date:
            date = (fields.Datetime.now() - timedelta(days=1000)).strftime(
                "%d/%m/%Y"
            )
        if not register_numbers:
            register_numbers = self.search(
                [("register_number", "!=", False)]
            ).mapped("register_number")
        params = {
            "fecha": date,
            "nregistro": list(set(register_numbers)),
            "pagina": 1,
        }

        r = requests.post(
            "https://cima.aemps.es/cima/rest/registroCambios", params=params,
        )
        r.raise_for_status()
        changes = r.json()

        results = changes["resultados"]
        while (
            params["pagina"] * changes["tamanioPagina"] < changes["totalFilas"]
        ):
            params["pagina"] += 1
            r = requests.post(
                "https://cima.aemps.es/cima/rest/registroCambios",
                params=params,
            )
            r.raise_for_status()
            changes = r.json()
            results += changes["resultados"]
        self.process_medication_changes(results)
