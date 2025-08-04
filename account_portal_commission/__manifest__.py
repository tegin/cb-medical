# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Account Portal Commission",
    "summary": """Add account restriction to portal users to see only their invoices
    and add route to show user commissions""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Dixmit, CreuBlanca",
    "website": "https://github.com/tegin/cb-medical",
    "depends": ["account", "account_commission", "portal", "cb_medical_commission"],
    "data": [
        "views/account_portal_templates.xml",
        "security/account_portal_security.xml",
        "security/ir.model.access.csv",
        "wizards/search_encounters_wizard_view.xml",
    ],
    "demo": [],
    "assets": {
        "web.assets_frontend": [
            "account_portal_commission/static/src/js/*.esm.js",
        ],
    },
}
