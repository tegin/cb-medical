import setuptools

setuptools.setup(
    setup_requires=['setuptools-odoo'],
    odoo_addon={
        "depends_override": {
            "cb_mgmtsystem_issue": "git+https://github.com/tegin/cb-addons.git@14.0#subdirectory=setup/cb_mgmtsystem_issue",
            "purchase_third_party": "git+https://github.com/tegin/cb-addons.git@14.0#subdirectory=setup/purchase_third_party",
        }
    },
)
