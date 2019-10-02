# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "CB Medical sequence configuration",
    "version": "11.0.1.0.0",
    "author": "Eficent, Creu Blanca",
    "depends": [
        "mrp",
        "cb_medical_block_request",
        "stock_pack_operation_auto_fill",
    ],
    "data": [
        "data/location_type_data.xml",
        "security/medical_security.xml",
        "security/ir.model.access.csv",
        "wizard/medical_encounter_medication_views.xml",
        "views/product_category_views.xml",
        "views/medical_encounter_views.xml",
        "views/res_partner_views.xml",
        "views/workflow_plan_definition_action.xml",
        "report/medical_encounter_medication_report.xml",
    ],
    "website": "https://github.com/OCA/vertical-medical",
    "license": "LGPL-3",
    "installable": True,
    "auto_install": False,
}
