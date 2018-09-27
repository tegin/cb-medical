# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class LaboratoryEvent(models.Model):
    _inherit = 'medical.laboratory.event'

    coverage_amount = fields.Float(required=True, default=0)
    private_amount = fields.Float(required=True, default=0)
