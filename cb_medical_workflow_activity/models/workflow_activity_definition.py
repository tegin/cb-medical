# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ActivityDefinition(models.Model):
    _inherit = 'workflow.activity.definition'

    service_id = fields.Many2one(
        'product.product',
        domain=[('type', '=', 'service')]
    )
    service_tmpl_id = fields.Many2one(
        'product.template',
        related='service_id.product_tmpl_id',
        readonly=True,
        store=True,
    )

    @api.constrains('service_id')
    def _check_product(self):
        for rec in self.filtered(lambda r: r.service_id):
            if rec.service_id.type != 'service':
                raise ValidationError(_(
                    'Activite are only allowed for services'
                ))
            if self.search([
                ('service_id', '=', rec.service_id.id)
            ], limit=1):
                raise ValidationError(_(
                    'Only one activity is allowed for service'
                ))
            if self.search([
                ('service_tmpl_id', '=', rec.service_tmpl_id.id)
            ], limit=1):
                raise ValidationError(_(
                    'Only one activity is allowed for service'
                ))
