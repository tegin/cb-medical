import setuptools

setuptools.setup(
    setup_requires=['setuptools-odoo'],
    odoo_addon={
        "depends_override": {
                "pos_safe_box": "git+https://github.com/tegin/cb-addons.git@14.0#subdirectory=setup/pos_safe_box",
                "web_flagbox": "git+https://github.com/tegin/cb-addons.git@14.0#subdirectory=setup/web_flagbox",
                "web_history_back": "git+https://github.com/tegin/cb-addons.git@14.0#subdirectory=setup/web_history_back",
            }
    },
)
