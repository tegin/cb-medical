# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _


class MedicalAgreementChangePrices(models.TransientModel):
    _name = "medical.agreement.change.prices"
    _description = 'medical.agreement.change.prices'

    difference = fields.Float(
        string="Indicate the percentage to apply to the agreement"
    )

    @api.multi
    def change_prices(self):
        context = dict(self._context or {})
        agreements = self.env["medical.coverage.agreement"].browse(
            context.get("active_ids")
        )
        for agreement in agreements:
            for item in agreement.item_ids:
                item.total_price = item.total_price + (
                    (item.total_price * self.difference) / 100
                )
            agreement.message_post(
                body=_("Prices have been changed by a %s &#037 by %s")
                % (self.difference, self.env.user.display_name)
            )
