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
        'sale_commission_formula',
        'sale_commission_cancel',
        'cb_medical_sale_invoice',
        'cb_medical_careplan_sale',
        'cb_medical_sale_invoice_group_method',
    ],
    'data': [
        'data/sale_commission_formula.xml',
        'views/account_invoice_view.xml',
        'views/res_partner_views.xml',
        'views/product_template_view.xml',
        'views/medical_laboratory_event_view.xml',
        'views/medical_procedure_request_view.xml',
        'views/medical_procedure_view.xml',
        'views/workflow_plan_definition_action.xml',
        'views/medical_encounter_views.xml',
        'wizard/wizard_settle.xml',
    ],
    'website': 'https://github.com/OCA/vertical-medical',
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
}
