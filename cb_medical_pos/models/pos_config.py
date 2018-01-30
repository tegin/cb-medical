# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    session_sequence_id = fields.Many2one(
        'ir.sequence',
        'Sequence for sessions'
    )
