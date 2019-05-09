# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class MedicalRole(models.Model):
    # FHIR Entity: PractitionerRole
    # (https://www.hl7.org/fhir/practitionerrole.html)
    _inherit = 'medical.role'

    specialty_required = fields.Boolean(
        default=False
    )
