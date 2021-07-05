from odoo import models


class MedicalCoverageAgreementXlsx(models.AbstractModel):
    _name = "report.medical_financial_coverage_agreement.mca_xlsx_private"
    _inherit = "report.medical_financial_coverage_agreement.mca_xlsx"
    _description = "Report CB Medical Financial Coverage Agreement Private"
