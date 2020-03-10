# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Cb Nonconformity Encounter",
    "summary": """
        CB custom nonconformity management""",
    "version": "11.0.1.0.0",
    "license": "AGPL-3",
    "author": "Creu Blanca",
    "website": "www.creublanca.es",
    "depends": ["cb_mgmtsystem_issue", "medical_administration_encounter"],
    "data": [
        "views/mgmtsystem_quality_issue.xml",
        "data/nonconformity_sequence_data.xml",
        "views/mgmtsystem_nonconformity_origin.xml",
        "wizards/wizard_create_nonconformity.xml",
        "views/medical_encounter.xml",
        "views/mgmtsystem_nonconformity.xml",
    ],
}
