# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MedicalSpecialty(models.Model):
    # FHIR Entity: PractitionerRole
    # (https://www.hl7.org/fhir/practitionerrole.html)
    _inherit = "medical.specialty"

    code = fields.Char(required=True)
    sequence_id = fields.Many2one(
        "ir.sequence", string="Sequence", required=True
    )
    sequence_number_next = fields.Integer(
        string="Next Number",
        help="The next sequence number will be used for the next invoice.",
        compute="_compute_seq_number_next",
        inverse="_inverse_seq_number_next",
    )

    @api.model
    def _sequence_vals(self, vals):
        return {
            "code": vals["code"].upper(),
            "prefix": vals["code"].upper(),
            "implementation": "no_gap",
            "name": vals["name"],
            "padding": 3,
            "number_increment": 1,
            "use_date_range": False,
        }

    @api.model
    def create(self, vals):
        if "sequence_id" not in vals:
            sequence = self.env["ir.sequence"].create(
                self._sequence_vals(vals)
            )
            vals["sequence_id"] = sequence.id
        return super(MedicalSpecialty, self).create(vals)

    # do not depend on 'sequence_id.date_range_ids', because
    # sequence_id._get_current_sequence() may invalidate it!
    @api.depends(
        "sequence_id.use_date_range", "sequence_id.number_next_actual"
    )
    def _compute_seq_number_next(self):
        """Compute 'sequence_number_next' according to the current sequence in use,
        an ir.sequence or an ir.sequence.date_range.
        """
        for record in self:
            sequence = record.sequence_id._get_current_sequence()
            record.sequence_number_next = sequence.number_next_actual

    def _inverse_seq_number_next(self):
        """Inverse 'sequence_number_next' to edit the current sequence next number."""
        for record in self:
            if record.sequence_id and record.sequence_number_next:
                sequence = record.sequence_id._get_current_sequence()
                sequence.number_next = record.sequence_number_next
