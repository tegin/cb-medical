# Copyright (C) 2017 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "CB Medical Requester",
    "version": "11.0.1.0.0",
    "category": "CB",
    "website": "https://creublanca.es",
    "author": "Creu Blanca",
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "summary": "CB medical location data",
    "depends": [
        "medical_administration_practitioner",
        "medical_workflow",
        "medical_clinical_careplan",
    ],
    "data": [
        "data/ir_sequence_data.xml",
        "security/medical_security.xml",
        "views/res_partner_views.xml",
        "views/medical_menu.xml",
        "wizard/medical_careplan_add_plan_definition_views.xml",
    ],
}
