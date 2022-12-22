# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Medical Coverage Request",
    "summary": "Medical financial coverage request",
    "version": "14.0.1.0.0",
    "author": "CreuBlanca, Eficent",
    "website": "https://github.com/tegin/cb-medical",
    "license": "AGPL-3",
    "depends": [
        "medical_clinical_request_group",
        "medical_clinical_procedure",
        "medical_administration_encounter_careplan",
        "medical_document",
        "medical_clinical_laboratory",
        "medical_financial_coverage_agreement",
        "medical_encounter_identifier",
    ],
    "data": [
        "views/medical_authorization_web.xml",
        "data/medical_authorization_method_data.xml",
        "data/medical_authorization_format_data.xml",
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
        "views/workflow_plan_definition.xml",
        "views/workflow_plan_definition_action.xml",
    ],
    "application": False,
    "installable": True,
    "auto_install": False,
}
