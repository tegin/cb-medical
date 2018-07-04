# Copyright 2017 LasLabs Inc.
# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Medical Invoices",
    "version": "11.0.1.0.0",
    "category": "Medical",
    "website": "https://github.com/OCA/vertical-medical",
    "author": "LasLabs, Creu Blanca, Eficent,"
              "Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "depends": [
        'cb_medical_careplan_sale',
        'account',
    ],
    "data": [
        'views/account_invoice_views.xml',
        'views/report_invoice.xml',
        'views/res_partner_views.xml',
        'views/sale_order_views.xml',
    ],
    "installable": True,
    "application": False,
}
