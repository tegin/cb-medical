# Copyright 2018 CreuBlanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalEncounterValidationAddService(models.TransientModel):
    _name = 'medical.encounter.validation.add.service'
    _inherit = 'medical.careplan.add.plan.definition'

    encounter_id = fields.Many2one(
        'medical.encounter',
        required=True
    )
    careplan_id = fields.Many2one(
        'medical.careplan',
        required=True,
    )

    def run(self):
        res = super(MedicalEncounterValidationAddService, self.with_context(
            on_validation=True
        ))._run()
        values = dict()
        query = res.get_sale_order_query()
        for el in query:
            key, partner, cov, is_ins, third_party, request = el
            if not values.get(key, False):
                values[key] = {}
            if not values[key].get(partner, False):
                values[key][partner] = {}
            if not values[key][partner].get(cov, False):
                values[key][partner][cov] = {}
            if not values[key][partner][cov].get(third_party, False):
                values[key][partner][cov][third_party] = []
            values[key][partner][cov][third_party].append(
                request.get_sale_order_line_vals(is_ins))
        self.encounter_id.generate_sale_orders(values)
        return
