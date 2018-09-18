# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    'name': 'CB Medical Views',
    'version': '11.0.1.0.0',
    'author': 'Eficent, Creu Blanca, Odoo Community Association (OCA)',
    'depends': [
        'medical_workflow',
        'medical_administration_encounter',
        'barcode_action',
        'medical_clinical_procedure',
        'l10n_es_partner',
    ],
    'data': [
        'views/medical_encounter.xml',
        'views/medical_event_view.xml',
        'views/medical_request_views.xml',
    ],
    'website': 'https://github.com/OCA/vertical-medical',
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
}
