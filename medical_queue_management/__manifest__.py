# Copyright 2023 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Medical Queue Management",
    "summary": """
        Manage patients with queue""",
    "version": "14.0.1.1.0",
    "license": "AGPL-3",
    "author": "CreuBlanca",
    "website": "https://github.com/tegin/cb-medical",
    "depends": ["queue_management", "cb_medical_careplan_sale"],
    "data": [
        "wizards/medical_careplan_add_plan_definition.xml",
        "views/queue_token_location.xml",
        "views/queue_token.xml",
        "views/res_partner_queue_location.xml",
        "views/res_partner.xml",
        "security/ir.model.access.csv",
        "views/queue_area.xml",
        "views/queue_location_area.xml",
        "views/workflow_plan_definition.xml",
        "views/medical_request_group.xml",
        "views/medical_encounter.xml",
        "templates/templates.xml",
    ],
    "demo": [],
    "qweb": ["static/src/xml/CopyClipboardListChar.xml"],
}
