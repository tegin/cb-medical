import setuptools

setuptools.setup(
    setup_requires=['setuptools-odoo'],
    odoo_addon={
        "depends_override": {
            "medical_terminology": "odoo14-addon-medical-terminology @ git+https://github.com/tegin/medical-fhir.git@14.0#subdirectory=setup/medical_terminology"
        }
    },
)
