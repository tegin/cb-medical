import logging
import math
from datetime import datetime

import requests

from odoo import api, models

_logger = logging.getLogger(__name__)


class MedicalCimaCron(models.AbstractModel):
    _name = "medical.cima.job"
    _description = "Tarea jon para actualizar medicamentos desde CIMA"

    @api.model
    def job_create_medicamento(self, codigo):
        try:
            self.env["medical.create.from.cima.wizard"].create_from_cima(codigo)
            _logger.info("Medicamento %s creado exitosamente", codigo)
        except Exception as e:
            _logger.error("Error creando medicamento %s: %s", codigo, str(e))
            raise  # para que el job pueda ser reintentado

    def actualizar_medicamentos_desde_cima(self, fecha_str=None):
        # Si no se pasa fecha, usar hoy
        if not fecha_str:
            fecha = datetime.today()
        else:
            try:
                # Espera formato 'd/m/Y', ej: '17/6/2025'
                fecha = datetime.strptime(fecha_str, "%d/%m/%Y")
            except ValueError:
                self._log("Error de formato en fecha", f"Fecha inválida: {fecha_str}")
                return

        fecha_param = fecha.strftime("%-d/%-m/%Y")  # formato requerido por la API
        url_base = "https://cima.aemps.es/cima/rest/registroCambios"
        codigos = set()

        # Primer request para saber cuántas páginas hay
        pagina = 1
        url = f"{url_base}?fecha={fecha_param}&pagina={pagina}"
        response = requests.get(url, timeout=15)
        if response.status_code != 200:
            self._log("Error consultando cambios", url, response.status_code)
            return

        data = response.json()
        total_filas = data.get("totalFilas", 0)
        tam_pagina = data.get("tamanioPagina", 200)
        numero_paginas = math.ceil(total_filas / tam_pagina) if tam_pagina else 1

        # Recolectar todos los códigos
        for pagina in range(1, numero_paginas + 1):
            url = f"{url_base}?fecha={fecha_param}&pagina={pagina}"
            response = requests.get(url, timeout=15)
            if response.status_code != 200:
                self._log("Error consultando página", url, response.status_code)
                continue

            data = response.json()
            resultados = data.get("resultados", [])
            for cambio in resultados:
                codigo = cambio.get("nregistro")
                if codigo:
                    codigos.add(codigo)

        self._log("Consulta finalizada", f"{len(codigos)} códigos recopilados")
        # Ejecutar jobs
        for codigo in codigos:
            self.env["medical.cima.job"].with_delay(
                priority=10, description=f"Crear medicamento {codigo}"
            ).job_create_medicamento(codigo)

        self._log("Jobs encolados", f"{len(codigos)} medicamentos")

    def _log(self, titulo, detalle, extra=""):
        self.env["ir.logging"].create(
            {
                "name": "CIMA Update",
                "type": "server",
                "level": "info",
                "dbname": self._cr.dbname,
                "message": f"{titulo}: {detalle} {extra}",
                "path": "medical.cima.cron",
                "func": "actualizar_medicamentos_desde_cima",
                "line": "0",
            }
        )
