# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    'name': 'PoS Validation',
    'version': '11.0.1.0.0',
    'category': 'Reporting',
    'website': 'https://github.com/eficent/cb-addons',
    'author': 'Creu Blanca, Eficent, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'summary': 'Validation of Careplans once they are assigned to a Session',
    'depends': [
        'cb_medical_pos',
        'pos_safe_box',
        'barcode_action',
        'cb_medical_commission',
        'cb_medical_cancel',
        'pos_session_pay_invoice',
        'cb_medical_sale_discount',
        'cb_medical_sale_invoice',
        'web_flagbox',
        'web_ir_actions_act_multi',
        'cb_medical_clinical_laboratory',
        'cb_medical_medication',
    ],
    'data': [
        'wizards/medical_encounter_validation_add_service.xml',
        'wizards/sale_order_line_cancel.xml',
        'data/medical_invoice_group.xml',
        'security/security.xml',
        'views/medical_encounter_view.xml',
        'views/administration_menu.xml',
        'views/pos_session_views.xml',
    ]
}
