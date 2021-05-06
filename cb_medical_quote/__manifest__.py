# Copyright 2018 Creu Blanca
# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "CB Medical Quote",
    "version": "12.0.1.0.0",
    "author": "Eficent, Creu Blanca",
    "depends": ["cb_medical_careplan_sale", "base_comment_template"],
    "category": "Medical",
    "data": [
        "wizards/wizard_create_quote_agreement.xml",
        "views/medical_coverage_agreement.xml",
        "security/medical_security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "views/medical_quote_views.xml",
        "views/medical_quote_layout_category_views.xml",
        "views/medical_menu.xml",
        "views/product_template_views.xml",
        "reports/medical_quote_templates.xml",
        "reports/medical_quote_report.xml",
        "data/mail_data.xml",
    ],
    "website": "https://github.com/Eficent/cb-addons",
    "license": "LGPL-3",
    "installable": True,
    "auto_install": False,
}
