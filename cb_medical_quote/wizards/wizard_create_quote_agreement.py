# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class WizardCreateQuoteAgreement(models.TransientModel):

    _name = "wizard.create.quote.agreement"
    _description = "wizard.create.quote.agreement"

    agreement_id = fields.Many2one("medical.coverage.agreement")

    possible_template_ids = fields.Many2many("medical.coverage.template")
    coverage_template_id = fields.Many2one(
        "medical.coverage.template",
        required=True,
        domain="[('id', 'in', possible_template_ids)]",
    )

    possible_center_ids = fields.Many2many("res.partner")
    center_id = fields.Many2one(
        "res.partner",
        required=True,
        domain="[('id', 'in', possible_center_ids)]",
    )

    @api.model
    def default_get(self, fields_list):
        rec = super().default_get(fields_list)
        agreement_id = self.env.context.get("active_id", False)
        rec["agreement_id"] = agreement_id
        agreement = self.env["medical.coverage.agreement"].browse(agreement_id)
        rec["possible_center_ids"] = [(6, 0, agreement.center_ids.ids)]
        rec["possible_template_ids"] = [(6, 0, agreement.coverage_template_ids.ids)]
        return rec

    def generate_quote(self):
        self.ensure_one()
        quote = self.env["medical.quote"].create(
            {
                "center_id": self.center_id.id,
                "coverage_template_id": self.coverage_template_id.id,
                "payor_id": self.coverage_template_id.payor_id.id,
                "origin_agreement_id": self.agreement_id.id,
            }
        )
        for item in self.agreement_id.item_ids:
            quote.add_agreement_line_id = item
            quote.button_add_line()

        action = self.env.ref("cb_medical_quote.action_quotes")
        result = action.read()[0]
        result["views"] = [(False, "form")]
        result["res_id"] = quote.id
        return result
