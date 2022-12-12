# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "CB Medical Invoice",
    "version": "13.0.1.0.0",
    "author": "Eficent, Creu Blanca",
    "depends": ["pos_validation", "account_invoice_supplier_self_invoice"],
    "data": [
        "security/medical_security.xml",
        "wizard/medical_encounter_change_partner_views.xml",
        "views/medical_encounter_views.xml",
        "views/report_self_invoice.xml",
        "views/res_company_views.xml",
        "views/res_partner_views.xml",
    ],
    "website": "https://github.com/tegin/cb-medical",
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
}
