import setuptools

setuptools.setup(
    setup_requires=['setuptools-odoo'],
    odoo_addon={
        "depends_override": {
                "sale_commission_cancel": "odoo14-addon-sale-commission-cancel @ git+https://github.com/tegin/cb-addons.git@14.0#subdirectory=setup/sale_commission_cancel",
            }
    },
)
