# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Medical Invoices",
    "version": "12.0.1.0.0",
    "category": "Medical",
    "website": "https://github.com/OCA/vertical-medical",
    "author": "Creu Blanca, Eficent",
    "license": "LGPL-3",
    "depends": ["cb_medical_sale_discount", "cb_sale_report_invoice"],
    "data": [
        "security/ir.model.access.csv",
        "views/account_invoice_views.xml",
        "views/report_invoice.xml",
        "views/nomenclature_menu.xml",
        "views/res_partner_views.xml",
        "views/sale_order_views.xml",
        "views/medical_coverage_agreement_view.xml",
        "views/medical_encounter_views.xml",
    ],
    "installable": True,
    "application": False,
}
