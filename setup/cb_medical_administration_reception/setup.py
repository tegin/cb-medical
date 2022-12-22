import setuptools

setuptools.setup(
    setup_requires=['setuptools-odoo'],
    odoo_addon={
        "depends_override": {
            "medical_administration_center": "git+https://github.com/tegin/medical-fhir.git@14.0#subdirectory=setup/medical_administration_center",
        }
    }
)
