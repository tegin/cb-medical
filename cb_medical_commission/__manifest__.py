# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Medical Commission',
    'summary': 'Add Commissions',
    'version': '11.0.1.0.0',
    'author': 'Eficent, Creu Blanca, Odoo Community Association (OCA)',
    'category': 'Medical',
    'depends': [
        'sale_commission',
        'sale_commission_formula',
        'medical_workflow',
        'medical_clinical_procedure',
    ],
    'data': [
        'data/sale_commission_formula.xml',
        'views/medical_practitioner_views.xml',
        'views/product_template_view.xml',
        'views/medical_procedure_request_view.xml',
        'views/medical_procedure_view.xml',
        'views/workflow_plan_definition_action.xml',
    ],
    'website': 'https://github.com/OCA/vertical-medical',
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
}
