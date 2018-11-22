# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class SaleOrder(models.AbstractModel):
    _inherit = 'sale.order'

    encounter_id = fields.Many2one('medical.encounter', readonly=True, )
    coverage_id = fields.Many2one('medical.coverage', readonly=True, )
    coverage_template_id = fields.Many2one(
        'medical.coverage.template', readonly=True,
        related='coverage_id.coverage_template_id'
    )
    coverage_agreement_id = fields.Many2one('medical.coverage.agreement')
    patient_id = fields.Many2one('medical.patient', readonly=True, )
    invoice_group_method_id = fields.Many2one(
        'invoice.group.method',
        readonly=True,
    )

    def create_third_party_move(self):
        if self.coverage_agreement_id:
            return
        return super().create_third_party_move()
