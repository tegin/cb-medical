# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "PoS Validation",
    "version": "14.0.1.0.0",
    "category": "Reporting",
    "website": "https://github.com/tegin/cb-medical",
    "author": "CreuBlanca, Eficent",
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "summary": "Validation of Careplans once they are assigned to a Session",
    "depends": [
        "pos_safe_box",
        "barcode_action",
        "cb_medical_cancel",
        "web_flagbox",
        "web_ir_actions_act_multi",
        "cb_medical_clinical_laboratory",
        "web_history_back",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "wizards/medical_encounter_validation_add_service.xml",
        "wizards/sale_order_line_cancel.xml",
        "data/medical_invoice_group.xml",
        "views/medical_encounter_view.xml",
        "views/administration_menu.xml",
        "views/pos_session_views.xml",
        "templates/templates.xml",
    ],
}
