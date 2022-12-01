import setuptools

setuptools.setup(
    setup_requires=['setuptools-odoo'],
    odoo_addon={
        "depends_override": {
                "sale_commission_cancel": "git+https://github.com/tegin/cb-addons.git@14.0#subdirectory=setup/sale_commission_cancel",
            }
    },
)
