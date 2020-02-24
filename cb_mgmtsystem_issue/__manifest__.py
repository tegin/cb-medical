# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Cb Mgmtsystem Issue',
    'summary': """
        Managemente System Issues""",
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Creu Blanca',
    'website': 'www.creublanca.es',
    'depends': [
        'mgmtsystem_nonconformity',
    ],
    'data': [
        'data/mgmtsystem_sequence.xml',
        'security/ir.model.access.csv',
        'security/msmsystem_security.xml',
        'views/mgmtsystem_quality_issue.xml',
    ],
}
