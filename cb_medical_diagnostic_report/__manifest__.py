# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Cb Medical Diagnostic Report",
    "summary": """Allows the creation of medical diagnostic reports""",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "author": "Creu Blanca",
    "website": "https://github.com/tegin/medical-fhir",
    "depends": [
        "medical_diagnostic_report",
        "medical_administration",
        "medical_signature_storage",
        "sequence_parser",
        "cb_medical_identifier",
        "web_drop_target",
        "web_tree_image_tooltip",
        "storage_file",
    ],
    "data": [
        "data/ir_parameter.xml",
        "security/department_security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "views/medical_department.xml",
        "views/medical_diagnostic_report_template.xml",
        "views/medical_diagnostic_report.xml",
        "views/medical_report_category.xml",
        "reports/medical_diagnostic_report_template.xml",
        "wizards/medical_diagnostic_report_expand.xml",
        "templates/assets.xml",
    ],
    "demo": ["demo/medical_diagnostic_report.xml"],
}
