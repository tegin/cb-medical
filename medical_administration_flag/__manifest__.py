# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Medical Patient Flag",
    "version": "14.0.1.0.0",
    "author": "Eficent, CreuBlanca",
    "depends": ["medical_base"],
    "data": [
        "data/ir_sequence_data.xml",
        "security/medical_security.xml",
        "security/ir.model.access.csv",
        "views/medical_patient_views.xml",
        "views/medical_flag_views.xml",
        "views/medical_flag_category_views.xml",
    ],
    "demo": [],
    "website": "https://github.com/tegin/cb-medical",
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
}
