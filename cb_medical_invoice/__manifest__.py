# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    'name': 'CB Medical sequence configuration',
    'version': '11.0.1.0.0',
    'author': 'Eficent, Creu Blanca, Odoo Community Association (OCA)',
    'depends': [
        'cb_medical_pos',
        'cb_medical_sale_invoice',
        'cb_medical_sale_invoice_group_method',
        'pos_validation',
        'sale',
    ],
    'data': [
        'security/medical_security.xml',
        'wizard/medical_encounter_change_partner_views.xml',
        'views/medical_encounter_views.xml',
        'views/res_company_views.xml',
    ],
    'website': 'https://github.com/OCA/vertical-medical',
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
}
