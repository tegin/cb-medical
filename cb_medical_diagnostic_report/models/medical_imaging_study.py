# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalImagingStudy(models.Model):
    # FHIR Entity: ImagingStudy (https://www.hl7.org/fhir/imagingstudy.html)
    _inherit = "medical.imaging.study"
    _description = "Medical Imaging Study"

    modality_ids = fields.Many2many(store=True)  # for searching purposes
