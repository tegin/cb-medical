from odoo import models


class MedicalCoverageAgreementXlsx(models.AbstractModel):
    _name = "report.cb_medical_financial_coverage_agreement.mca_xlsx"
    _inherit = "report.report_xlsx.abstract"

    def tree_height(self, item):
        return (
            1
            if not item["childs"]
            else max([self.tree_height(child) for child in item["childs"]]) + 1
        )

    def generate_sub_tree(self, workbook, sheet, level, item, i, th):
        bold = workbook.add_format({"bold": True})
        name = (
            "%s - %s"
            % (item["category"].display_name, item["category"].description)
            if item["category"].description
            else item["category"].display_name
        )
        sheet.write(i, level, name, bold)
        i += 1
        bold = workbook.add_format({"bold": False})
        for child in item["data"]:
            nomenclature = (
                "%s [%s]"
                % (child["nomenclature"].code, child["product"].default_code)
                if child["nomenclature"]
                else (child["product"].default_code or "")
            )
            sheet.write(i, level + 1, nomenclature, bold)
            sheet.write(i, level + 2, child["product"].name, bold)
            sheet.write(
                i, th + 3, str(child["item"].coverage_price) + " €", bold
            )
            i += 1

        for child in item["childs"]:
            sheet, i = self.generate_sub_tree(
                workbook, sheet, level + 1, child, i, th
            )
        return sheet, i

    def generate_xlsx_report(self, workbook, data, agreements):
        for agreement in agreements:
            report_name = agreement.name
            sheet = workbook.add_worksheet(report_name[:31])
            items = agreement._agreement_report_data()
            i = 0
            if items:
                th = max([self.tree_height(item) for item in items])
                for item in items:
                    level = 0
                    sheet, i = self.generate_sub_tree(
                        workbook, sheet, level, item, i, th
                    )
