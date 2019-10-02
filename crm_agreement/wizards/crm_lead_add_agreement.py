# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class CrmLeadAddAgreement(models.TransientModel):

    _name = "crm.lead.add.agreement"

    lead_id = fields.Many2one("crm.lead", required=True)
    coverage_template_ids = fields.One2many(
        comodel_name="medical.coverage.template",
        related="lead_id.partner_id.commercial_partner_id"
        ".coverage_template_ids",
        readonly=True,
    )
    agreement_id = fields.Many2one("medical.coverage.agreement", required=True)

    @api.multi
    def doit(self):
        self.ensure_one()
        self.lead_id.write({"agreement_ids": [(4, self.agreement_id.id)]})
        return {}
