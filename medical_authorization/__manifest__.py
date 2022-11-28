# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Medical Authorization",
    "summary": "Medical financial coverage request",
    "version": "14.0.1.0.0",
    "author": "CreuBlanca, Eficent",
    "website": "https://github.com/tegin/cb-medical",
    "license": "AGPL-3",
    "depends": ["medical_financial_coverage_request"],
    "data": [
        "security/ir.model.access.csv",
        "wizards/medical_request_group_uncheck_authorization.xml",
        "views/medical_authorization_method_view.xml",
        "wizards/medical_request_group_check_authorization_views.xml",
    ],
    "application": False,
    "installable": True,
    "auto_install": False,
}
