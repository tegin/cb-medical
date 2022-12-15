# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "CB Medical Invoice",
    "version": "14.0.1.0.0",
    "author": "Eficent, CreuBlanca",
    "depends": [
        "pos_validation",
        "account_invoice_supplier_self_invoice",
        "account_move_change_company",
        "account_reconciliation_widget",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/medical_encounter_change_partner_views.xml",
        "views/medical_encounter_views.xml",
        "views/res_company_views.xml",
    ],
    "website": "https://github.com/tegin/cb-medical",
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
}
