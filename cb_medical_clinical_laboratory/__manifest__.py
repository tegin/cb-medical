# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Medical documents',
    'version': '11.0.1.0.0',
    'author': 'Eficent, Creu Blanca, Odoo Community Association (OCA)',
    'depends': [
        'medical_workflow',
        'medical_clinical_laboratory',
        'cb_medical_medication',
    ],
    'data': [
        'security/medical_security.xml',
        'security/ir.model.access.csv',
        'views/medical_coverage_template_views.xml',
        'views/medical_laboratory_event_view.xml',
        'views/medical_laboratory_request_view.xml',
        'views/workflow_activity_definition_views.xml',
        'views/medical_laboratory_service_view.xml',
    ],
    'website': 'https://github.com/OCA/cb-addons',
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
}
