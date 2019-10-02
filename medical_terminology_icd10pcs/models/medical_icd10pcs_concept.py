# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MedicalICD10PCSConcept(models.Model):
    """
        Medical ATC concept
        (https://www.hl7.org/fhir/terminologies-systems.html)
        It has been defined following the code system entity with the following
        information:
        - url: http://www.whocc.no/atc
        - identifier: urn:oid:2.16.840.1.113883.6.73
        - name: ATC/DDD
        - publisher: WHO
    """

    _name = "medical.icd10pcs.concept"
    code = fields.Char(compute="_compute_code", store=True, required=False)
    section_id = fields.Many2one("medical.icd10pcs.section", required=True)
    body_system_id = fields.Many2one(
        "medical.icd10pcs.body.system",
        required=True,
        domain="[('section_id', '=', section_id)]",
    )
    root_operation_id = fields.Many2one(
        "medical.icd10pcs.operation",
        required=True,
        domain="[('section_id', '=', section_id)]",
    )
    body_part_id = fields.Many2one(
        "medical.icd10pcs.body.part",
        required=True,
        domain="[('body_system_id', '=', body_system_id)]",
    )
    approach_id = fields.Many2one("medical.icd10pcs.approach", required=True)
    device_id = fields.Many2one(
        "medical.icd10pcs.device",
        required=True,
        domain="[('section_id', '=', section_id)]",
    )
    qualifier_id = fields.Many2one(
        "medical.icd10pcs.qualifier",
        required=True,
        domain="[('section_id', '=', section_id)]",
    )
    name = fields.Char(required=True, translate=True)

    @api.depends(
        "section_id",
        "body_system_id",
        "root_operation_id",
        "body_part_id",
        "approach_id",
        "device_id",
        "qualifier_id",
    )
    def _compute_code(self):
        for rec in self:
            rec.code = "%s%s%s%s%s%s%s" % (
                rec.section_id.code,
                rec.body_system_id.code,
                rec.root_operation_id.code,
                rec.body_part_id.code,
                rec.approach_id.code,
                rec.device_id.code,
                rec.qualifier_id.code,
            )
