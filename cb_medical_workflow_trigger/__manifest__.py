# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Medical Workflow Triggers",
    "version": "12.0.1.0.0",
    "author": "Eficent, Creu Blanca",
    "depends": ["cb_medical_workflow_plandefinition"],
    "data": [
        "security/medical_security.xml",
        "security/ir.model.access.csv",
        "views/workflow_plan_definition_action.xml",
    ],
    "website": "https://github.com/OCA/vertical-medical",
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
}
