import setuptools

setuptools.setup(
    setup_requires=['setuptools-odoo'],
    odoo_addon={
    "depends_override": {
            "cb_sale_report_invoice": "git+https://github.com/tegin/cb-addons.git@14.0#subdirectory=setup/cb_sale_report_invoice",
            "sale_third_party": "git+https://github.com/tegin/cb-addons.git@14.0#subdirectory=setup/sale_third_party",
        }
    },
)
