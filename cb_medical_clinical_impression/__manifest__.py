# Copyright 2023 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Cb Medical Clinical Impression",
    "summary": """
        CB Impressions""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "CreuBlanca,Odoo Community Association (OCA)",
    "website": "https://github.com/tegin/cb-medical",
    "depends": [
        "medical_clinical_impression",
        "medical_product_request",
        "cb_medical_diagnostic_report",
    ],
    "data": [
        "templates/assets.xml",
        "templates/report.xml",
        "views/medical_patient.xml",
        "data/cron.xml",
        "views/medical_clinical_impression.xml",
    ],
    "qweb": [
        "static/src/xml/medical_impression_view.xml",
    ],
}
