import logging
import math
from datetime import datetime, timedelta

import requests

from odoo import api, models

_logger = logging.getLogger(__name__)


class MedicalCimaCron(models.AbstractModel):
    _name = "medical.cima.job"
    _description = "Job to update medications from CIMA"

    @api.model
    def job_update_medicamento(self, codigo):
        try:
            self.env["medical.create.from.cima.wizard"].create_from_cima(
                codigo, override=True
            )
            _logger.info("Medicament %s created successfully", codigo)
        except Exception as e:
            _logger.error("Error in medication creation %s: %s", codigo, str(e))
            raise

    def update_medication_from_cima(self, date_str=None):
        # If not date_str, use yesterday's date
        if not date_str:
            date = datetime.today() - timedelta(days=1)
        else:
            try:
                date = datetime.strptime(date_str, "%d/%m/%Y")
            except ValueError:
                self._log("Date format error", f"Invalid date: {date_str}")
                return

        date_param = date.strftime("%-d/%-m/%Y")
        url_base = "https://cima.aemps.es/cima/rest/registroCambios"
        codigos = set()

        # First request to know how many pages there are
        pagina = 1
        url = f"{url_base}?fecha={date_param}&pagina={pagina}"
        response = requests.get(url, timeout=30)
        if response.status_code != 200:
            self._log("Error consultando cambios", url, response.status_code)
            return

        data = response.json()
        total_filas = data.get("totalFilas", 0)
        tam_pagina = data.get("tamanioPagina", 200)
        numero_paginas = math.ceil(total_filas / tam_pagina) if tam_pagina else 1

        # Recollect all codes
        for pagina in range(1, numero_paginas + 1):
            url = f"{url_base}?fecha={date_param}&pagina={pagina}"
            response = requests.get(url, timeout=30)
            if response.status_code != 200:
                self._log("Error", url, response.status_code)
                continue

            data = response.json()
            resultados = data.get("resultados", [])
            for cambio in resultados:
                codigo = cambio.get("nregistro")
                if codigo:
                    codigos.add(codigo)

        self._log("Request completed", f"{len(codigos)} codes retrieved")
        # Ejecutar jobs
        for codigo in codigos:
            self.env["medical.cima.job"].with_delay(
                priority=10, description=f"Create medicament {codigo}"
            ).job_update_medicamento(codigo)

        self._log("Enqueued jobs ", f"{len(codigos)} medicaments")

    def _log(self, titulo, detalle, extra=""):
        self.env["ir.logging"].create(
            {
                "name": "CIMA Update",
                "type": "server",
                "level": "info",
                "dbname": self._cr.dbname,
                "message": f"{titulo}: {detalle} {extra}",
                "path": "medical.cima.cron",
                "func": "update_medication_from_cima",
                "line": "0",
            }
        )
