# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Medical Patient second lastname',
    'version': '11.0.1.0.0',
    'author': 'Eficent, Creu Blanca',
    'depends': [
        'medical_administration_firstname',
        'partner_second_lastname',
    ],
    'data': [
        'views/medical_patient_views.xml',
    ],
    'website': 'https://github.com/OCA/cb-addons',
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
}
