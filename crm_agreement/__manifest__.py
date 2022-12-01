# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Crm Agreement",
    "summary": """
        Link of Medical Agreements and CRM""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "CreuBlanca,Odoo Community Association (OCA)",
    "website": "https://github.com/tegin/cb-medical",
    "depends": [
        "sale_crm",
        "cb_medical_quote",
        "medical_financial_coverage_agreement",
        "cb_medical_administration_requester",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/mail_data.xml",
        "views/medical_quote.xml",
        "wizards/crm_lead_add_agreement.xml",
        "views/medical_coverage_agreement.xml",
        "views/crm_lead.xml",
    ],
}
