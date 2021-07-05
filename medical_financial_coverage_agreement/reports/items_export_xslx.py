from odoo import models


class MedicalCoverageAgreementItem(models.AbstractModel):

    _name = "report.medical_financial_coverage_agreement.items_xslx"
    _description = "Report CB Medical Financial Coverage Agreement Items"
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, items):
        sheet = workbook.add_worksheet("Medical Coverage Items")
        bold = workbook.add_format({"bold": True})
        sheet.set_column(0, 2, 30)
        sheet.set_column(3, 6, 15)
        sheet.write(0, 0, "Internal Reference", bold)
        sheet.write(0, 1, "Service", bold)
        sheet.write(0, 2, "Category", bold)
        sheet.write(0, 3, "Plan Definition", bold)
        sheet.write(0, 4, "Total Price", bold)
        sheet.write(0, 5, "Coverage %", bold)
        sheet.write(0, 6, "Coverage Price", bold)
        sheet.write(0, 7, "Private Price", bold)
        for i, item in enumerate(items):
            i += 1
            sheet.write(i, 0, item.default_code)
            sheet.write(i, 1, item.product_id.name)
            category = item.categ_id.display_name if (item.categ_id) else ""
            sheet.write(i, 2, category)
            plan_definition = (
                item.plan_definition_id.display_name
                if (item.plan_definition_id)
                else ""
            )
            sheet.write(i, 3, plan_definition)
            sheet.write(i, 4, item.total_price)
            sheet.write(i, 5, item.coverage_percentage)
            sheet.write(i, 6, item.coverage_price)
            sheet.write(i, 7, item.private_price)
