# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "CB Medical sequence configuration",
    "version": "14.0.1.0.0",
    "author": "Eficent, CreuBlanca",
    "depends": [
        "medical_administration_encounter_careplan",
        "medical_clinical_careplan",
        "medical_clinical_request_group",
        "medical_clinical_procedure",
        "medical_medication_request",
        "medical_document",
        "medical_clinical_laboratory",
        "sequence_parser",
        "medical_diagnostic_report",
        "medical_administration_center",
        # "sequence_safe",
    ],
    "demo": ["demo/medical_demo.xml"],
    "data": [
        "data/config_parameter.xml",
        "views/res_partner_views.xml",
        "views/medical_encounter_view.xml",
    ],
    "website": "https://github.com/tegin/cb-medical",
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
    "external_dependencies": {"python": ["numpy", "pandas", "bokeh==2.3.1"]},
}
