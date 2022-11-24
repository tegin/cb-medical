import setuptools

setuptools.setup(
    setup_requires=['setuptools-odoo'],
    odoo_addon={
    "depends_override": {
            "cb_mgmtsystem_issue": "git+https://github.com/tegin/cb-addons.git@14.0#subdirectory=setup/cb_mgmtsystem_issue",
             "medical_administration_encounter": "git+https://github.com/tegin/medical-fhir.git@14.0#subdirectory=setup/medical_administration_encounter"
        }
    },
)
