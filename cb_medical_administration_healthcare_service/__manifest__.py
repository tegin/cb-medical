# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Medical Patient Healthcare Service CB",
    "version": "12.0.1.0.0",
    "author": "Eficent, Creu Blanca",
    "depends": [
        "medical_administration_healthcare_service",
        "cb_medical_administration_practitioner_specialty",
    ],
    "data": ["views/res_partner_views.xml"],
    "website": "https://github.com/OCA/cb-addons",
    "license": "LGPL-3",
    "installable": True,
    "auto_install": False,
}
