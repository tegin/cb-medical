# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Medical Administration Practitioner Specialty",
    "version": "13.0.1.0.0",
    "author": "Eficent, Creu Blanca",
    "category": "Medical",
    "website": "https://github.com/tegin/cb-medical",
    "license": "AGPL-3",
    "depends": ["medical_administration_practitioner_specialty"],
    "data": [
        "data/medical_role.xml",
        "views/res_partner_views.xml",
        "views/medical_role.xml",
        "views/medical_specialty.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
