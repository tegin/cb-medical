# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class MedicalPractitioner(models.Model):
    _inherit = 'medical.practitioner'

    commission_agent_ids = fields.Many2many(
        string='Commission agents',
        comodel_name='res.partner',
    )
