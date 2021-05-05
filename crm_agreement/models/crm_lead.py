# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import ast

from odoo import api, fields, models


class CrmLead(models.Model):
    _inherit = "crm.lead"

    @api.model
    def _default_agreements(self):
        if not self.env.context.get("agreement_id"):
            return False
        return [(4, self.env.context.get("agreement_id"))]

    agreement_ids = fields.Many2many(
        "medical.coverage.agreement",
        relation="medical_coverage_agreement_crm_lead",
        column1="lead_id",
        column2="agreement_id",
        string="Agreements",
        default=lambda r: r._default_agreements(),
    )
    agreement_count = fields.Integer(compute="_compute_agreement_count")
    is_payor = fields.Boolean(
        related="partner_id.commercial_partner_id.is_payor", readonly=True
    )
    medical_quote_ids = fields.One2many(
        "medical.quote", inverse_name="lead_id"
    )
    medical_quote_count = fields.Integer(
        compute="_compute_medical_quote_count"
    )

    @api.depends("medical_quote_ids")
    def _compute_medical_quote_count(self):
        for record in self:
            record.medical_quote_count = len(record.medical_quote_ids)

    @api.depends("agreement_ids")
    def _compute_agreement_count(self):
        for record in self:
            record.agreement_count = len(record.agreement_ids)

    @api.multi
    def view_agreements(self):
        self.ensure_one()
        action = self.env.ref(
            "cb_medical_financial_coverage_agreement."
            "medical_coverage_agreement_action"
        ).read()[0]
        action["context"] = ast.literal_eval(action["context"])
        action["context"]["lead_id"] = self.id
        action["domain"] = [("id", "in", self.agreement_ids.ids)]
        if len(self.agreement_ids) == 1:
            action["res_id"] = self.agreement_ids.id
            action["views"] = [(False, "form")]
        return action

    @api.multi
    def view_medical_quotes(self):
        self.ensure_one()
        action = self.env.ref("cb_medical_quote.action_quotes").read()[0]
        action["context"] = ast.literal_eval(action["context"])
        action["context"].update(
            {
                "default_lead_id": self.id,
                "default_is_private": False,
                "default_payor_id": self.partner_id.commercial_partner_id.id,
            }
        )
        action["domain"] = [("lead_id", "=", self.id)]
        if len(self.medical_quote_ids) == 1:
            action["res_id"] = self.medical_quote_ids.id
            action["views"] = [(False, "form")]
        return action

    def _onchange_partner_id_values(self, partner_id):
        result = super()._onchange_partner_id_values(partner_id)
        agreement_ids = []
        if partner_id and not self.env.context.get("agreement_id"):
            partner = self.env["res.partner"].browse(partner_id)
            templates = partner.commercial_partner_id.coverage_template_ids
            for agreement in self.agreement_ids:
                if any(
                    template in templates
                    for template in agreement.coverage_template_ids
                ):
                    agreement_ids.append(agreement.id)
            result["agreement_ids"] = [(6, 0, agreement_ids)]
        return result

    def _generate_quote_context(self):
        return {
            "default_payor_id": self.partner_id.commercial_partner_id.id,
            "default_lead_id": self.id,
        }

    def generate_quote(self):
        action = self.env.ref("cb_medical_quote.action_quotes").read()[0]
        action.update(
            {
                "view_mode": "form",
                "views": [(False, "form")],
                "target": "new",
                "context": self._generate_quote_context(),
            }
        )
        return action
