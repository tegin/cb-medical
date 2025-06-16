# Copyright 2025 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Cb Medical Cima Data",
    "description": """
        Importa medicamentos desde CIMA""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "CreuBlanca",
    "depends": ["queue_job", "cb_medical_product_request"],
    "data": [
        "wizards/medical_create_from_cima_wizard.xml",
        "data/cron.xml",
    ],
    "demo": [],
}
