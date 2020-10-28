# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "CB Medical link to PoS",
    "version": "12.0.1.0.0",
    "author": "Eficent, Creu Blanca",
    "depends": [
        "pos_session_pay_invoice",
        "pos_close_approval",
        "cb_medical_commission",
        "account_cash_invoice_inter_company",
    ],
    "data": [
        "data/ir_sequence_data.xml",
        "security/cb_medical_pos_security.xml",
        "wizard/wizard_medical_encounter_close_view.xml",
        "wizard/wizard_medical_encounter_finish_view.xml",
        "wizard/wizard_medical_encounter_add_amount_view.xml",
        "views/res_company_views.xml",
        "views/medical_encounter_views.xml",
        "views/pos_config_views.xml",
        "views/sale_order_views.xml",
        "views/pos_session_views.xml",
        "views/report_invoice.xml",
    ],
    "website": "https://github.com/OCA/cb-addons",
    "license": "LGPL-3",
    "installable": True,
    "auto_install": False,
}
