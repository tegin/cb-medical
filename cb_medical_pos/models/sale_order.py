# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    pos_session_id = fields.Many2one(
        comodel_name='pos.session',
        string='PoS Session',
        readonly=1,
    )
    is_down_payment = fields.Boolean(
        default=False
    )
