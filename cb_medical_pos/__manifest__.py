# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "CB Medical link to PoS",
    "version": "14.0.1.0.0",
    "author": "Eficent, CreuBlanca",
    "depends": [
        "pos_session_pay_invoice",
        "cb_medical_commission",
        "pos_inter_company",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/product_medical_center_company.xml",
        "views/product_template.xml",
        "views/pos_order.xml",
        "views/pos_payment.xml",
        "data/ir_sequence_data.xml",
        "wizard/wizard_medical_encounter_close_view.xml",
        "wizard/wizard_medical_encounter_finish_view.xml",
        "wizard/wizard_medical_encounter_add_amount_view.xml",
        "views/res_company_views.xml",
        "views/medical_encounter_views.xml",
        "views/pos_config_views.xml",
        "views/sale_order_views.xml",
        "views/pos_session_views.xml",
        "views/report_invoice.xml",
        "reports/report_pos_payment.xml",
    ],
    "website": "https://github.com/tegin/cb-medical",
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
}
