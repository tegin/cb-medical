# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Medical Coverage Request',
    'summary': 'Medical financial coverage request',
    'version': '11.0.1.0.0',
    'author': 'Creu Blanca, Eficent, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/vertical-medical',
    'license': 'LGPL-3',
    'depends': [
        'medical_clinical_careplan',
        'cb_medical_workflow_plandefinition',
        'cb_medical_financial_coverage_agreement'
    ],
    'data': [
        'data/medical_authorization_method_data.xml',
        'data/medical_authorization_format_data.xml',
        'security/medical_security.xml',
        'security/ir.model.access.csv',
        'views/medical_request_views.xml',
        'views/medical_coverage_agreement_item_view.xml',
        'views/medical_coverage_agreement_view.xml',
        'views/medical_authorization_format_view.xml',
        'wizard/medical_careplan_add_plan_definition_views.xml',
    ],
    'demo': [
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
