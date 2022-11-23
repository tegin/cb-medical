# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Medical Financial Coverage Agreement",
    "version": "13.0.1.0.0",
    "author": "Eficent, Creu Blanca",
    "category": "Medical",
    "depends": [
        "medical_financial_coverage",
        "medical_administration_center",
        "medical_workflow",
        "product_nomenclature",
        "report_xlsx",
        "report_context",
    ],
    "website": "https://github.com/tegin/cb-medical",
    "license": "AGPL-3",
    "data": [
        "wizards/medical_agreement_expand.xml",
        "security/medical_security.xml",
        "wizards/medical_coverage_agreement_join.xml",
        "reports/items_export_xslx.xml",
        "reports/agreement_report.xml",
        "reports/agreement_compare_report.xml",
        "reports/medical_coverage_agreement_xlsx.xml",
        "reports/medical_coverage_agreement_xlsx_private.xml",
        "data/medical_coverage_agreement.xml",
        "wizards/medical_coverage_agreement_template_views.xml",
        "wizards/medical_agreement_change_prices_views.xml",
        "views/medical_coverage_agreement_item_view.xml",
        "views/medical_coverage_agreement_view.xml",
        "views/medical_coverage_template_view.xml",
        "views/medical_menu.xml",
        "views/product_views.xml",
        "views/workflow_plan_definition_views.xml",
        "views/product_category_views.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
    "auto_install": False,
}
