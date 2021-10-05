# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Medical Sale Invoice Group Method",
    "version": "13.0.1.0.1",
    "author": "Eficent, Creu Blanca",
    "category": "Medical",
    "depends": [
        "medical_base",
        "cb_medical_careplan_sale",
        "barcodes",
        "barcode_action",
        "medical_administration_encounter",
    ],
    "data": [
        "views/medical_authorization_method.xml",
        "data/medical_invoice_group.xml",
        "data/medical_preinvoice_group_sequence.xml",
        "security/medical_security.xml",
        "security/ir.model.access.csv",
        "views/medical_preinvoice_group_menu.xml",
        "views/report_invoice.xml",
        "wizard/wizard_sale_preinvoice_group_views.xml",
        "wizard/invoice_sales_by_group_view.xml",
        "views/medical_preinvoice_group_line_view.xml",
        "views/res_company_views.xml",
        "views/sale_order_view.xml",
        "views/medical_coverage_agreement_item_view.xml",
        "views/medical_preinvoice_group_views.xml",
        "report/medical_preinvoice_group.xml",
    ],
    "website": "https://github.com/OCA/vertical-medical",
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
}
