# Copyright 2024 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalClinicalImpressionTemplate(models.Model):

    _inherit = "medical.clinical.impression.template"

    concept_ids = fields.One2many(
        comodel_name="medical.clinical.impression.template.concept",
        inverse_name="template_id",
    )


class MedicalClinicalImpressionTemplateConcept(models.Model):
    _name = "medical.clinical.impression.template.concept"

    _order = "sequence asc"
    template_id = fields.Many2one("medical.clinical.impression.template", required=True)
    sequence = fields.Integer(default=20)
    concept_id = fields.Many2one(
        comodel_name="medical.observation.concept", required=True
    )
