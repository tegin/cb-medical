# Copyright 2022 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Cb Medical Product Request",
    "summary": """
        This addon expands the medical_product_request fhir
        definition adapting it to the spanish prescription system""",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "author": "Creu Blanca,Odoo Community Association (OCA)",
    "website": "www.creublanca.es",
    "depends": [
        "medical_product_request",
        "medical_encounter_identifier",
        "cb_medical_administration_requester",
        "web_domain_field",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/medical_product_product.xml",
        "views/medical_product_template.xml",
        "views/medical_product_template_commercial.xml",
        "views/medical_product_product_commercial.xml",
        "views/medical_product_request.xml",
        "views/medical_product_request_order.xml",
        "views/res_config_settings_views.xml",
        "templates/assets.xml",
        "data/data.xml",
        "reports/spanish_prescription.xml",
        "reports/spanish_prescription_template.xml",
    ],
    "demo": ["demo/medical_product_request_demo.xml"],
}
