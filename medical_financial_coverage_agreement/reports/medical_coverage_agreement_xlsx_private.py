from odoo import models


class MedicalCoverageAgreementXlsx(models.AbstractModel):
    _name = "report.cb_medical_financial_coverage_agreement.mca_xlsx_private"
    _inherit = "report.cb_medical_financial_coverage_agreement.mca_xlsx"
