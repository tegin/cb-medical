# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Medical Cancel",
    "version": "14.0.1.0.0",
    "author": "Eficent, CreuBlanca",
    "category": "Medical",
    "depends": ["cb_medical_pos"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/medical_request_cancel_views.xml",
        "wizard/medical_careplan_cancel_views.xml",
        "wizard/medical_laboratory_request_cancel_views.xml",
        "wizard/medical_procedure_request_cancel_views.xml",
        "wizard/medical_request_group_cancel_views.xml",
        "wizard/medical_encounter_cancel_views.xml",
        "views/medical_sale_discount_views.xml",
        "views/medical_request_views.xml",
        "views/medical_careplan_view.xml",
        "views/medical_laboratory_request_view.xml",
        "views/medical_procedure_request_view.xml",
        "views/medical_request_group_view.xml",
        "views/medical_encounter_view.xml",
    ],
    "website": "https://github.com/tegin/cb-medical",
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
}
