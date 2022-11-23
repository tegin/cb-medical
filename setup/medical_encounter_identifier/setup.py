import setuptools

setuptools.setup(
    setup_requires=['setuptools-odoo'],
    odoo_addon={
        "depends_override": {
            "medical_administration_encounter_careplan": "git+https://github.com/tegin/medical-fhir.git@14.0#subdirectory=setup/medical_administration_encounter_careplan",
            "medical_clinical_careplan": "git+https://github.com/tegin/medical-fhir.git@14.0#subdirectory=setup/medical_clinical_careplan",
            "medical_clinical_request_group": "git+https://github.com/tegin/medical-fhir.git@14.0#subdirectory=setup/medical_clinical_request_group",
            "medical_clinical_procedure": "git+https://github.com/tegin/medical-fhir.git@14.0#subdirectory=setup/medical_clinical_procedure",
            "medical_medication_request": "git+https://github.com/tegin/medical-fhir.git@14.0#subdirectory=setup/medical_medication_request",
            "medical_diagnostic_report": "git+https://github.com/tegin/medical-fhir.git@14.0#subdirectory=setup/medical_diagnostic_report",
            "sequence_parser": "git+https://github.com/tegin/cb-addons.git@14.0#subdirectory=setup/sequence_parser",
        }
    },
)
