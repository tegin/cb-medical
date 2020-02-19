# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Medical Coverage Request",
    "summary": "Medical financial coverage request",
    "version": "12.0.1.0.0",
    "author": "Creu Blanca, Eficent",
    "website": "https://github.com/tegin/cb_addons",
    "license": "LGPL-3",
    "depends": [
        "cb_medical_workflow_plandefinition",
        "cb_medical_financial_coverage_agreement",
        "cb_medical_identifier",
    ],
    "data": [
        "data/medical_authorization_method_data.xml",
        "data/medical_authorization_format_data.xml",
        "security/medical_security.xml",
        "security/ir.model.access.csv",
        "views/medical_authorization_method_view.xml",
        "wizard/medical_careplan_add_plan_definition_views.xml",
        "wizard/medical_request_group_change_plan_views.xml",
        "wizard/medical_request_group_check_authorization_views.xml",
        "views/res_partner_views.xml",
        "views/medical_request_views.xml",
        "views/medical_request_group_views.xml",
        "views/medical_coverage_agreement_item_view.xml",
        "views/medical_coverage_agreement_view.xml",
        "views/medical_coverage_template_view.xml",
        "views/medical_authorization_format_view.xml",
    ],
    "application": False,
    "installable": True,
    "auto_install": False,
}
