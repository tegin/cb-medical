# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MedicalCoverageAgreementJoin(models.TransientModel):
    _name = "medical.coverage.agreement.join"
    _description = "medical.coverage.agreement.join"

    def _default_agreements(self):
        context = self.env.context
        return self.env[context.get("active_model")].browse(
            context.get("active_ids")
        )

    agreement_ids = fields.Many2many(
        "medical.coverage.agreement", default=_default_agreements
    )

    def check_possible_join(self):
        company = self.agreement_ids.mapped("company_id")
        if len(company) > 1:
            raise ValidationError(_("The company must be the same"))
        coverages = self.agreement_ids.mapped("coverage_template_ids")
        centers = self.agreement_ids.mapped("center_ids")
        for agreement in self.agreement_ids:
            if coverages != agreement.coverage_template_ids:
                raise ValidationError(_("The templates must be the same"))
            if centers != agreement.center_ids:
                raise ValidationError(_("The centers must be the same"))

    @api.multi
    def run(self):
        if len(self.agreement_ids) < 2:
            raise ValidationError(_("You must select multiple agreements"))
        self.check_possible_join()
        final_agreement = self.agreement_ids[0]
        for agreement in self.agreement_ids[1:]:
            agreement.item_ids.write(
                {"coverage_agreement_id": final_agreement.id}
            )
            if agreement.active:
                agreement.toggle_active()
            agreement.message_post(
                body=_("Joined to agreement %s")
                % (final_agreement.display_name)
            )
            final_agreement.message_post(
                body=_("Joined items from agreement %s")
                % (agreement.display_name)
            )
        return
