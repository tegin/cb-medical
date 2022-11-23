# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Medical Turn Management",
    "summary": """
        Manage Profesional turn management""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "CreuBlanca,Odoo Community Association (OCA)",
    "website": "https://github.com/tegin/cb-medical",
    "depends": [
        "medical_administration_practitioner",
        "web_view_calendar_list",
        "medical_base",
        "medical_administration_center",
        "mail",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/medical_menu.xml",
        "wizards/wzd_medical_turn.xml",
        "views/res_partner.xml",
        "views/medical_turn_specialty.xml",
        "views/medical_turn.xml",
        "views/medical_turn_tag.xml",
    ],
}
