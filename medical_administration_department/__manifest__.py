# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Medical Administration Department',
    'description': """
        This module allows to create and modify departments""",
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Creu Blanca',
    'website': 'https://github.com/tegin/medical-fhir',
    'depends': ["medical_administration",
    ],
    'data': [
        "security/department_security.xml",
        "data/ir_sequence_data.xml",
        "views/res_partner.xml",
    ],
    'demo': [
        'demo/res_partner.xml',
    ],
}
