# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    'name': 'CB Medical link to PoS',
    'version': '11.0.1.0.0',
    'author': 'Eficent, Creu Blanca, Odoo Community Association (OCA)',
    'depends': [
        'cb_medical_careplan_sale',
        'point_of_sale',
        'pos_session_pay_invoice',
        'pos_close_approval',
        'pos_multiple_sessions',
    ],
    'data': [
        'data/ir_sequence_data.xml',
        'wizard/wizard_medical_careplan_close_view.xml',
        'wizard/wizard_medical_careplan_add_amount_view.xml',
        'views/medical_careplan_views.xml',
        'views/pos_config_views.xml',
        'views/sale_order_views.xml',
        'views/pos_session_views.xml',
    ],
    'website': 'https://github.com/OCA/cb-addons',
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
}
