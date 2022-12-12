# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Medical Clinical Laboratory",
    "version": "14.0.1.0.0",
    "author": "Eficent, CreuBlanca",
    "depends": ["cb_medical_medication"],
    "data": [
        "security/ir.model.access.csv",
        "views/medical_coverage_template_views.xml",
        "views/medical_laboratory_event_view.xml",
        "views/medical_laboratory_request_view.xml",
        "views/workflow_activity_definition_views.xml",
        "views/medical_laboratory_service_view.xml",
    ],
    "website": "https://github.com/tegin/cb-medical",
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
}
