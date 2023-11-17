# Copyright 2023 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Medical Queue Management",
    "summary": """
        Manage patients with queue""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "CreuBlanca",
    "website": "https://github.com/tegin/cb-medical",
    "depends": ["queue_management", "medical_financial_coverage_request"],
    "data": [
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
    ],
    "demo": [],
}
