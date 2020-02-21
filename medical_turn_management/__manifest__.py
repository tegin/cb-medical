# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Medical Turn Management',
    'summary': """
        Manage Profesional turn management""",
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Creu Blanca,Odoo Community Association (OCA)',
    'website': 'www.creublanca.es',
    'depends': [
        'medical_administration_practitioner',
        'web_view_calendar_list',
        'medical_clinical',
        'cb_medical_administration_center',
    ],
    'data': [
        'security/medical_security.xml',
        'security/ir.model.access.csv',
        'views/medical_menu.xml',
        'wizards/wzd_medical_turn.xml',
        'views/res_partner.xml',
        'views/medical_turn_specialty.xml',
        'views/medical_turn.xml',
    ],
    'installable': False
}
