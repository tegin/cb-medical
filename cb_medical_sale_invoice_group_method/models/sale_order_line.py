# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    _order = 'sequence'

    preinvoice_group_id = fields.Many2one(
        string='Pre-invoice Group',
        comodel_name='sale.preinvoice.group',
    )
    preinvoice_status = fields.Selection(
        related='preinvoice_group_id.state'
    )
    is_validated = fields.Boolean()
    sequence = fields.Integer(
        string='Sequence',
        default='999999',
    )

    @api.model
    @api.onchange('sequence')
    def create(self, vals):
        if vals.get('sequence', '999999') == '999999':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'sale.order.line') or '/'
        return super(SaleOrderLine, self).create(vals)

    @api.multi
    def validate_line(self):
        self.ensure_one()
        self.preinvoice_group_id.validate_line(self)
