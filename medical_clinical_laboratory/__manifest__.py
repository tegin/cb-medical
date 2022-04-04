# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Medical Laboratory",
    "version": "14.0.1.0.0",
    "author": "Eficent, CreuBlanca",
    "depends": ["medical_administration_encounter_careplan"],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "views/medical_request_views.xml",
        "views/medical_laboratory_event_view.xml",
        "views/medical_laboratory_request_view.xml",
        "views/medical_laboratory_sample_view.xml",
    ],
    "website": "https://github.com/tegin/cb-medical",
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
}
