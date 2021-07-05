# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class MedicalLaboratoryEvent(models.Model):
    # FHIR Entity: Procedure (https://www.hl7.org/fhir/procedure.html)
    _name = 'medical.laboratory.event'
    _description = 'Medical Laboratory Event'
    _inherit = 'medical.event'

    internal_identifier = fields.Char(
        string="Laboratory Event"
    )
    laboratory_request_id = fields.Many2one(
        comodel_name='medical.laboratory.request',
        string='Laboratory request',
        ondelete='restrict', index=True,
        readonly=True,
    )   # FHIR Field: BasedOn

    def _get_internal_identifier(self, vals):
        return self.env['ir.sequence'].next_by_code(
            'medical.laboratory.event') or '/'
