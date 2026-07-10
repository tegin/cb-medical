# Copyright 2025 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Cb Medical Cima Data",
    "version": "16.0.1.0.0",
    "installable": True,
    "website": "https://github.com/tegin/cb-medical",
    "license": "AGPL-3",
    "author": "CreuBlanca",
    "depends": ["cb_medical_product_request", "queue_job"],
    "external_dependencies": {
        "python": ["pandas"],
    },
    "data": [
        # "views/medical_product_template_commercial.xml",
        "views/medical_product_template.xml",
        "views/medical_product_product.xml",
        # "views/medical_product_product_commercial.xml",
        "security/ir.model.access.csv",
        "wizards/medical_create_from_cima_wizard.xml",
        "data/cron.xml",
        "data/queue.xml",
    ],
    "demo": [],
}
