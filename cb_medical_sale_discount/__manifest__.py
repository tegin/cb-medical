# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Medical Sale Discounts",
    "version": "12.0.1.0.0",
    "author": "Eficent, Creu Blanca",
    "category": "Medical",
    "depends": ["cb_medical_careplan_sale", "decimal_precision"],
    "data": [
        "security/medical_security.xml",
        "security/ir.model.access.csv",
        "wizard/medical_request_group_discount_views.xml",
        "views/medical_request_views.xml",
        "views/medical_request_group_views.xml",
        "views/medical_sale_discount_views.xml",
    ],
    "website": "https://github.com/eficent/cb-addons",
    "license": "LGPL-3",
    "installable": True,
    "auto_install": False,
}
