# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    'name': 'CB Testing',
    'version': '11.0.1.0.0',
    'author': 'Eficent, Creu Blanca, Odoo Community Association (OCA)',
    'depends': [
        'cb_medical_careplan_sale',
        'medical_document_zpl2',
        'pos_validation',
        'cb_medical_views',
        'cb_medical_identifier',
        'cb_medical_sale_invoice_group_method',
        'cb_medical_medication',
        'cb_medical_cancel',
        'cb_medical_state_update',
        'cb_medical_block_request',
        'cb_medical_authorization',
        'cb_medical_medication',
        'cb_medical_workflow_activity',
        'cb_medical_invoice',
    ],
    'data': [
    ],
    'website': 'https://github.com/OCA/vertical-medical',
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
}
