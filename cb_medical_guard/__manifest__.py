# Copyright (C) 2018 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "CB Medical Guard",
    "version": "14.0.1.0.0",
    "category": "CB",
    "website": "https://github.com/tegin/cb-medical",
    "author": "CreuBlanca, Eficent",
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "summary": "CB medical location data",
    "depends": ["cb_medical_commission"],
    "data": [
        "security/medical_security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "views/medical_menu.xml",
        "wizard/medical_guard_invoice_views.xml",
        "wizard/medical_guard_plan_apply_views.xml",
        "views/medical_guard_views.xml",
        "views/medical_guard_plan_views.xml",
        "views/res_partner_views.xml",
        "views/account_move_views.xml",
    ],
}
