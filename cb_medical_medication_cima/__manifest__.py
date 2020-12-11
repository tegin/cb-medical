# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Cb Medical Medication CIMA",
    "summary": """
        Get Medication from CIMA""",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": "Creu Blanca",
    "website": "www.creublanca.es",
    "depends": ["cb_medical_medication"],
    "data": [
        "data/ir_cron_data.xml",
        "data/mail_channel_data.xml",
        "views/product_template.xml",
        "views/product_product.xml",
        "wizards/wizard_create_medication.xml",
    ],
}
