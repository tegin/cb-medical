import setuptools

setuptools.setup(
    setup_requires=['setuptools-odoo'],
    odoo_addon={
    "depends_override": {
            "remote_report_to_printer_label": "git+https://github.com/tegin/cb-addons.git@14.0#subdirectory=setup/remote_report_to_printer_label",
            "medical_clinical_procedure": "git+https://github.com/tegin/medical-fhir.git@14.0#subdirectory=setup/medical_clinical_procedure"
        }
    },
)
