# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Medical ICD-10-PCS Codification",
    "summary": "Medical codification base",
    "version": "14.0.1.0.0",
    "author": "CreuBlanca, Eficent",
    "category": "Medical",
    "website": "https://github.com/tegin/cb-medical",
    "license": "AGPL-3",
    "depends": ["medical_terminology"],
    "data": [
        "security/ir.model.access.csv",
        "views/medical_cie10pcs_concept_views.xml",
    ],
    "application": False,
    "installable": True,
    "auto_install": False,
}
