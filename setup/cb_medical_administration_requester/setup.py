import setuptools

setuptools.setup(
    setup_requires=['setuptools-odoo'],
    odoo_addon={
        "depends_override": {
             "medical_administration_practitioner": "odoo14-addon-medical-administration-practitioner @ git+https://github.com/tegin/medical-fhir.git@14.0#subdirectory=setup/medical_administration_practitioner",
             "medical_workflow": "odoo14-addon-medical-workflow @ git+https://github.com/tegin/medical-fhir.git@14.0#subdirectory=setup/medical_workflow",
             "medical_clinical_careplan": "odoo14-addon-medical-clinical-careplan @ git+https://github.com/tegin/medical-fhir.git@14.0#subdirectory=setup/medical_clinical_careplan"

        }
    },
)
