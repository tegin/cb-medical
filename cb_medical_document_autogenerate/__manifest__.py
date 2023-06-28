# Copyright 2023 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Cb Medical Document Autogenerate",
    "summary": """
        medical document autogenerate""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "CreuBlanca",
    "website": "https://github.com/tegin/cb-medical",
    "depends": [
        "medical_document",
    ],
    "data": [
        "views/medical_document_template.xml",
        "views/medical_document_reference.xml",
    ],
    "demo": [],
    "post_init_hook": "post_init_hook",
}
