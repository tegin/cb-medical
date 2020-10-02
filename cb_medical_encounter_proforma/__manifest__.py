# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Cb Medical Encounter Proforma",
    "description": """
        Add pro forma invoice to encounters""",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": "Creu Blanca",
    "website": "www.creublanca.es",
    "depends": [
        "cb_medical_careplan_sale",
        "document_quick_access",
        "report_qr",
    ],
    "data": ["reports/medical_encounter_proforma_report.xml"],
}
