import setuptools

setuptools.setup(
    setup_requires=['setuptools-odoo'],
    odoo_addon={
    "depends_override": {
            "cb_sale_report_invoice": "odoo14-addon-medical-cb-sale-report-invoice @ git+https://github.com/tegin/cb-addons.git@14.0#subdirectory=setup/cb_sale_report_invoice",
            "sale_third_party": "odoo14-addon-medical-sale-third-party @ git+https://github.com/tegin/cb-addons.git@14.0#subdirectory=setup/sale_third_party",
        }
    },
)
