import setuptools

setuptools.setup(
    setup_requires=['setuptools-odoo'],
    odoo_addon={
        "depends_override": {
            "medical_financial_coverage": "odoo14-addon-medical-financial-coverage @ git+https://github.com/tegin/medical-fhir.git@14.0#subdirectory=setup/medical_financial_coverage",
            "medical_workflow": "odoo14-addon-medical-workflow @ git+https://github.com/tegin/medical-fhir.git@14.0#subdirectory=setup/medical_workflow",
            "product_nomenclature": "odoo14-addon-product-nomenclature @ git+https://github.com/tegin/cb-addons.git@14.0#subdirectory=setup/product_nomenclature",
            "medical_administration_center": "odoo14-addon-medical-administration-center @ git+https://github.com/tegin/medical-fhir.git@14.0#subdirectory=setup/medical_administration_center",
        }
    },
)
