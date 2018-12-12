# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _


class MedicalAgreementChangePrices(models.TransientModel):
    _name = 'medical.agreement.change.prices'

    difference = fields.Float(
        string="Indicate the percentage to apply to the selected item(s):",
    )

    @api.multi
    def change_prices(self):
        context = dict(self._context or {})
        items = self.env['medical.coverage.agreement.item'].browse(context.get(
            'active_ids'))
        agreement = items[0].coverage_agreement_id
        list_items = ""
        count = 0
        for item in items:
            item.total_price = item.total_price + ((item.total_price *
                                                    self.difference) / 100)
            count += 1
            if len(items) > count:
                list_items = list_items + item.display_name + ', '
            else:
                list_items = list_items + _("and ") + item.display_name + '.'
        agreement.message_post(
            body=_("Prices have been changed by a %s &#037 by %s in %s") %
                  (self.difference, self.env.user.display_name, list_items),
        )
        result = {
            "type": "ir.actions.act_window",
            "res_model": "medical.coverage.agreement.item",
            "domain": [("coverage_agreement_id", "=", agreement.id)],
            "name": "Agreement Items",
        }
        result['views'] = [(False, "tree"), (False, "form")]
        return result
