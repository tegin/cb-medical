# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    commission_agent_ids = fields.Many2many(
        string='Commission agents',
        relation="commission_agent_rel",
        column1="partner_id",
        column2="agent_id",
        comodel_name='res.partner',
        domain="[('agent', '=', True)]"
    )
    practitioner_condition_ids = fields.One2many(
        'medical.practitioner.condition',
        inverse_name='practitioner_id',
        copy=False
    )
