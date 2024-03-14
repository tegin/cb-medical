# Copyright 2023 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import requests

from odoo import fields, models


class MedicalCimaLog(models.Model):

    _name = "medical.cima.log"
    _description = "Medical Cima Log"  # TODO

    date = fields.Date(required=True)
    url = fields.Char(required=True)
    page = fields.Integer(required=True, default=1)

    def _get_changes(self):
        result = requests.get(
            "%sregistroCambios" % self.url,
            params={"fecha": self.date.strftime("%d/%m/%Y"), "pagina": self.page},
        )
        result.raise_for_status()
        return result.json()

    def cron_update_medication(self):
        record = self.search([], limit=1)
        changes = record._get_changes()
        while True:
            for result in changes["resultados"]:
                if result["nregistro"]:
                    record.with_delay()._update_medication_registry(result["nregistro"])
            record.page += 1
            self.env.cr.commit()  # pylint: disable=E8102
            if changes["totalFilas"] < changes["pagina"] * changes["tamanioPagina"]:
                break
            changes = record._get_changes()
        record.write({"page": 1, "date": fields.Date.today()})

    def _get_presentation_info(self, registry_number, page):
        result = requests.get(
            "%spresentaciones" % self.url,
            params={"nregistro": registry_number, "pagina": self.page},
        )
        result.raise_for_status()
        return result.json()

    def _update_medication_registry(self, registry_number):
        page = 1
        presentations = self._get_presentation_info(registry_number, page)
        while True:
            for result in presentations["resultados"]:
                if "dcp" not in result:
                    continue
                self.env["medical.product.product.commercial"].with_context(
                    active_test=False
                )._import_cima_data(
                    result,
                    requests.get(
                        "%smedicamento" % self.url, params={"cn": result["cn"]}
                    ).json(),
                )
            page += 1
            presentations = self._get_presentation_info(registry_number, page)
            if (
                presentations["totalFilas"]
                < presentations["pagina"] * presentations["tamanioPagina"]
            ):
                break
