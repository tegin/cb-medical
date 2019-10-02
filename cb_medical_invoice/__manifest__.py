# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "CB Medical sequence configuration",
    "version": "11.0.1.0.0",
    "author": "Eficent, Creu Blanca",
    "depends": ["pos_validation"],
    "data": [
        "security/medical_security.xml",
        "wizard/medical_encounter_change_partner_views.xml",
        "views/medical_encounter_views.xml",
        "views/res_company_views.xml",
    ],
    "website": "https://github.com/OCA/vertical-medical",
    "license": "LGPL-3",
    "installable": True,
    "auto_install": False,
}
