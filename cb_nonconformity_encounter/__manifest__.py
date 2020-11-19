# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Cb Nonconformity Encounter",
    "summary": """
        CB custom nonconformity management""",
    "version": "12.0.1.1.0",
    "license": "AGPL-3",
    "author": "Creu Blanca",
    "website": "www.creublanca.es",
    "depends": ["cb_mgmtsystem_issue", "medical_administration_encounter"],
    "data": [
        "wizards/wizard_create_nonconformity_encounter.xml",
        "views/mgmtsystem_nonconformity_origin.xml",
        "views/medical_encounter.xml",
    ],
}
