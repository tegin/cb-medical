# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "CB Medical Views",
    "version": "14.0.1.0.0",
    "author": "Eficent, CreuBlanca",
    "depends": [
        "account",
        "barcode_action",
        "cb_medical_careplan_sale",
        "l10n_es_partner",
        "l10n_es",
    ],
    "data": [
        "security/medical_encounter_create_group.xml",
        "views/account_invoice_view.xml",
        "views/medical_encounter.xml",
        "views/medical_event_view.xml",
        "views/medical_patient_views.xml",
        "views/medical_request_views.xml",
        "views/medical_menu.xml",
        "views/res_partner_views.xml",
        "views/sale_order_view.xml",
    ],
    "website": "https://github.com/tegin/cb-medical",
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
}
