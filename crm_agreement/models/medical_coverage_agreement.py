# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MedicalCoverageAgreement(models.Model):

    _inherit = "medical.coverage.agreement"

    def _default_leads(self):
        if not self.env.context.get("lead_id"):
            return False
        return [(4, self.env.context["lead_id"])]

    def _default_coverage_template(self):
        if not self.env.context.get("lead_id"):
            return False
        partner = (
            self.env["crm.lead"]
            .browse(self.env.context["lead_id"])
            .partner_id.commercial_partner_id
        )
        return [(6, 0, partner.coverage_template_ids.ids)]

    lead_ids = fields.Many2many(
        "crm.lead",
        relation="medical_coverage_agreement_crm_lead",
        column1="agreement_id",
        column2="lead_id",
        string="Leads",
        default=lambda r: r._default_leads(),
        copy=False,
    )
    coverage_template_ids = fields.Many2many(
        default=lambda r: r._default_coverage_template()
    )
    lead_count = fields.Integer(compute="_compute_lead_count")

    @api.depends("lead_ids")
    def _compute_lead_count(self):
        for record in self:
            record.lead_count = len(record.lead_ids)

    def view_leads(self):
        self.ensure_one()
        action = self.env.ref("crm.crm_lead_opportunities").read()[0]
        action["domain"] = [("agreement_ids", "=", self.id)]
        action["context"] = {
            "default_type": "opportunity",
            "agreement_id": self.id,
        }
        partners = self.coverage_template_ids.mapped("payor_id")
        if len(partners) == 1:
            action["context"]["default_partner_id"] = partners.id
        if len(self.lead_ids) == 1:
            action["res_id"] = self.lead_ids.id
            action["views"] = [(False, "form")]
        return action
