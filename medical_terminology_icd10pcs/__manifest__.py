# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Medical ICD-10-PCS Codification",
    "summary": "Medical codification base",
    "version": "12.0.1.0.0",
    "author": "Creu Blanca, Eficent",
    "category": "Medical",
    "website": "https://github.com/OCA/vertical-medical",
    "license": "AGPL-3",
    "depends": ["medical_terminology"],
    "data": [
        "security/medical_icd10pcs_qualifier.xml",
        "security/medical_icd10pcs_device.xml",
        "security/medical_icd10pcs_approach.xml",
        "security/medical_icd10pcs_body_part.xml",
        "security/medical_icd10pcs_operation.xml",
        "security/medical_icd10pcs_system.xml",
        "security/medical_icd10pcs_section.xml",
        "security/medical_icd10pcs_concept.xml",
        "security/medical_security.xml",
        "security/ir.model.access.csv",
        "views/medical_cie10pcs_concept_views.xml",
    ],
    "application": False,
    "installable": True,
    "auto_install": False,
}
