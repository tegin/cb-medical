# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Medical documents",
    "version": "13.0.1.0.0",
    "author": "Eficent, Creu Blanca",
    "depends": [
        "medical_document",
        "printer_zpl2",
        "remote_report_to_printer_label",
    ],
    "data": [
        "views/medical_document_type_views.xml",
        "views/medical_document_reference_views.xml",
    ],
    "website": "https://github.com/tegin/cb-medical",
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
}
