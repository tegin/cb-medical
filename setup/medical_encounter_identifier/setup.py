import setuptools

setuptools.setup(
    setup_requires=['setuptools-odoo'],
    odoo_addon={
        "depends_override": {
            "medical_administration_encounter_careplan": "odoo14-addon-medical-administration-encounter-careplan @ git+https://github.com/tegin/medical-fhir.git@14.0#subdirectory=setup/medical_administration_encounter_careplan",
            "medical_clinical_careplan": "odoo14-addon-medical-clinical-careplan @ git+https://github.com/tegin/medical-fhir.git@14.0#subdirectory=setup/medical_clinical_careplan",
            "medical_clinical_request_group": "odoo14-addon-medical-clinical-request-group @ git+https://github.com/tegin/medical-fhir.git@14.0#subdirectory=setup/medical_clinical_request_group",
            "medical_clinical_procedure": "odoo14-addon-medical-clinical-procedure @ git+https://github.com/tegin/medical-fhir.git@14.0#subdirectory=setup/medical_clinical_procedure",
            "medical_medication_request": "odoo14-addon-medical-medication-request @ git+https://github.com/tegin/medical-fhir.git@14.0#subdirectory=setup/medical_medication_request",
            "medical_diagnostic_report": "odoo14-addon-medical-diagnostic-report @ git+https://github.com/tegin/medical-fhir.git@14.0#subdirectory=setup/medical_diagnostic_report",
            "sequence_parser": "odoo14-addon-sequence-parser @ git+https://github.com/tegin/cb-addons.git@14.0#subdirectory=setup/sequence_parser",
            "medical_administration_center": "odoo14-addon-medical-administration-center @ git+https://github.com/tegin/medical-fhir.git@14.0#subdirectory=setup/medical_administration_center",
        }
    },
)
