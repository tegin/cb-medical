import setuptools

setuptools.setup(
    setup_requires=['setuptools-odoo'],
    odoo_addon={
        "depends_override": {
            "medical_financial_coverage": "git+https://github.com/tegin/medical-fhir.git@14.0#subdirectory=setup/medical_financial_coverage",
            "medical_workflow": "git+https://github.com/tegin/medical-fhir.git@14.0#subdirectory=setup/medical_workflow",
            "product_nomenclature": "git+https://github.com/tegin/cb-addons.git@14.0#subdirectory=setup/product_nomenclature",
            "medical_administration_center": "git+https://github.com/tegin/medical-fhir.git@14.0#subdirectory=setup/medical_administration_center",
        }
    },
)
