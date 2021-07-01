# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Medical documents",
    "version": "13.0.1.0.0",
    "author": "Eficent, Creu Blanca",
    "depends": [
        "medical_workflow",
        "medical_clinical",
        "remote_report_to_printer",
    ],
    "data": [
        "security/medical_security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "data/medical_workflow.xml",
        "wizard/medical_document_reference_change_language_views.xml",
        "wizard/medical_document_type_add_language_views.xml",
        "views/medical_request_views.xml",
        "views/medical_document_reference_views.xml",
        "views/medical_document_template_views.xml",
        "views/medical_document_type_views.xml",
        "views/workflow_activity_definition.xml",
        "report/document_report.xml",
    ],
    "website": "https://github.com/OCA/cb-addons",
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
}
