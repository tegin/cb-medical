# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import fields, models


class MedicalAgreementExpand(models.TransientModel):

    _name = "medical.agreement.expand"
    _description = "TODO"

    agreement_id = fields.Many2one("medical.coverage.agreement", required=True)
    name = fields.Char(required=True)
    difference = fields.Float(
        string="Indicate the percentage to apply to the agreement"
    )
    date_to = fields.Date(required=True)

    def _get_copy_vals(self):
        return {
            "parent_id": self.agreement_id.id,
            "name": self.name,
            "date_from": self.agreement_id.date_to + timedelta(days=1),
            "date_to": self.date_to,
            "coverage_template_ids": [
                (6, 0, self.agreement_id.coverage_template_ids.ids)
            ],
        }

    def _expand(self):
        self.ensure_one()
        new_agreement = self.agreement_id.copy(self._get_copy_vals())
        self.env["medical.agreement.change.prices"].create(
            {"difference": self.difference}
        ).with_context(
            active_ids=new_agreement.ids,
            active_model=new_agreement._name,
            active_id=new_agreement.id,
        ).change_prices()
        return new_agreement

    def expand(self):
        return self._expand().get_formview_action()
