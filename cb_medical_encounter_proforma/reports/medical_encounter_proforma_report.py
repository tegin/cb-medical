from odoo import api, models


class MedicalEncounterProformaReport(models.AbstractModel):
    _name = "report.cb_medical_encounter_proforma.report_encounter_proforma"
    _description = "Proforma Encounter Report"

    def get_lines_data(self, encounter):
        return encounter.get_sale_order_lines()

    @api.model
    def _get_report_values(self, docids, data=None):
        encounter_id = self.env["medical.encounter"].browse(docids)
        encounter_id.ensure_one()
        lines = self.get_lines_data(encounter_id)
        proforma_datas = []
        for key in lines.keys():
            company_id = (
                self.env.user.company_id
                if key == 0
                else self.env["medical.coverage.agreement"]
                .browse(key)
                .company_id
            )
            for partner in lines[key].keys():
                pid = self.env["res.partner"].browse(partner)
                for coverage in lines[key][partner].keys():
                    for third_party in lines[key][partner][coverage].keys():
                        is_third_party = bool(third_party)
                        tpp = False
                        if not is_third_party:
                            tpp = self.env["res.partner"].browse(third_party)
                        product_lines = lines[key][partner][coverage][
                            third_party
                        ]
                        lines_data = []
                        for product_line in product_lines:
                            product_id = self.env["product.product"].browse(
                                product_line["product_id"]
                            )
                            taxes = product_id.taxes_id.filtered(
                                lambda r: not company_id
                                or r.company_id == company_id
                            )
                            price = taxes.compute_all(
                                product_line["price_unit"],
                                company_id.currency_id,
                                product_line["product_uom_qty"],
                                product=product_id,
                                partner=encounter_id.patient_id,
                            )
                            taxes = ", ".join(taxes.mapped("name"))
                            new_line = {
                                "product_id": product_id,
                                "product_qty": product_line["product_uom_qty"],
                                "price_unit": product_line["price_unit"],
                                "taxes": taxes,
                                "price_total": price["total_included"],
                            }
                            lines_data.append(new_line)
                        encounter_identifier = "%s_%s_%s_%s_%s" % (
                            encounter_id.internal_identifier,
                            key,
                            partner,
                            coverage or 0,
                            third_party,
                        )
                        proforma_datas.append(
                            {
                                # 'o': encounter_id,
                                "partner": pid,
                                "encounter_identifier": encounter_identifier,
                                "is_third_party": is_third_party,
                                "third_party_partner": tpp,
                                "company": encounter_id.company_id
                                or self.env.user.company_id,
                                "lines_data": lines_data,
                            }
                        )

        return {"proforma_datas": proforma_datas, "encounter": encounter_id}


class MedicalEncounterProformaReportPrivate(models.AbstractModel):
    _name = "report.cb_medical_encounter_proforma.report_encounter_proforma_private"
    _inherit = "report.cb_medical_encounter_proforma.report_encounter_proforma"
    _table = "report_encounter_proforma_private"
    _description = "Proforma Encounter Report"

    def get_lines_data(self, encounter):
        return {0: encounter.get_sale_order_lines()[0]}


class MedicalEncounterProformaReportPayor(models.AbstractModel):
    _name = (
        "report.cb_medical_encounter_proforma.report_encounter_proforma_payor"
    )
    _inherit = "report.cb_medical_encounter_proforma.report_encounter_proforma"
    _table = "report_encounter_proforma_payor"
    _description = "Proforma Encounter Report"

    def get_lines_data(self, encounter):
        lines = encounter.get_sale_order_lines()
        lines.pop(0, None)
        return lines
