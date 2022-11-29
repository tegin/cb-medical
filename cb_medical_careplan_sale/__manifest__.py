# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Medical Careplan to sales",
    "version": "14.0.1.0.0",
    "author": "Eficent, CreuBlanca",
    "category": "Medical",
    "depends": [
        "sale_third_party",
        "medical_authorization",
        "cb_sale_report_invoice",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/medical_invoice_group.xml",
        "data/medical_sub_payor_sequence.xml",
        "wizard/medical_careplan_add_plan_definition_views.xml",
        "wizard/medical_encounter_add_careplan.xml",
        "wizard/medical_request_group_discount_views.xml",
        "reports/sale_report_templates.xml",
        "views/account_invoice_views.xml",
        "views/nomenclature_menu.xml",
        "views/report_invoice.xml",
        "views/medical_request_group_view.xml",
        "views/medical_encounter_views.xml",
        "views/medical_request_views.xml",
        "views/medical_laboratory_event_view.xml",
        "views/res_partner_views.xml",
        "views/res_config_settings_views.xml",
        "views/medical_coverage_agreement_view.xml",
        "views/medical_authorization_method_view.xml",
        "views/sale_order_views.xml",
        "views/medical_sale_discount_views.xml",
    ],
    "website": "https://github.com/tegin/cb-medical",
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
}
