# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class MedicalRequest(models.AbstractModel):
    # FHIR Entity: Request (https://www.hl7.org/fhir/request.html)
    _inherit = 'medical.request'
    order_by_id = fields.Many2one(
        domain=[('is_requester', '=', True)]
    )
