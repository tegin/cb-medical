# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Medical Careplan to sales',
    'version': '11.0.1.0.0',
    'author': 'Eficent, Creu Blanca, Odoo Community Association (OCA)',
    'category': 'Medical',
    'depends': [
        'medical_clinical_careplan',
        'medical_clinical_procedure',
        'sale',
        'cb_medical_financial_coverage_request',
        'cb_medical_workflow_plandefinition',
    ],
    'data': [
        'views/medical_careplan_views.xml',
        'views/medical_request_views.xml',
    ],
    'website': 'https://github.com/eficent/cb-addons',
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
}
