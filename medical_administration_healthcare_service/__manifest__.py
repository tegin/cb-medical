# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Medical Patient Healthcare Service",
    "version": "12.0.1.0.0",
    "author": "Eficent, Creu Blanca",
    "depends": ["medical_administration_practitioner"],
    "data": [
        "data/ir_sequence_data.xml",
        "security/medical_security.xml",
        "views/res_partner_views.xml",
        "views/medical_menu.xml",
    ],
    "website": "https://github.com/OCA/cb-addons",
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
}
