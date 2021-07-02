# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Medical Signature Storage",
    "summary": """
        Store User signature""",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "author": "Creu Blanca,Odoo Community Association (OCA)",
    "website": "creublanca.es",
    "depends": [
        # 'medical_diagnostic_report',
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizards/res_users_update_signature.xml",
        "views/res_users_view.xml",
    ],
    "demo": [],
}
