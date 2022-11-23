from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.base.models.ir_sequence import _update_nogap


class MedicalEncounter(models.Model):
    _inherit = "medical.encounter"

    center_id = fields.Many2one(
        "res.partner",
        domain=[("is_center", "=", True)],
        required=True,
        track_visibility=True,
    )
    location_id = fields.Many2one(required=False, default=False, invisible=1)

    internal_identifier_prefix = fields.Char(readonly=True, copy=False)
    internal_identifier_value = fields.Integer(default=0, readonly=True, copy=False)
    internal_identifier_suffix = fields.Char(readonly=True, copy=False)
    internal_identifier_dc = fields.Char(readonly=True, copy=False)

    number_next = fields.Integer(default=1, copy=False)
    # We must keep this name in order to use _update_nogap function

    @api.model
    def create(self, vals):
        if vals.get("internal_identifier_value", 0) == 0:
            pf, val, suf, dc, identifier = self._get_identifier_values(vals)
            vals["internal_identifier_prefix"] = pf
            vals["internal_identifier_value"] = val
            vals["internal_identifier_suffix"] = suf
            vals["internal_identifier_dc"] = dc
            vals["internal_identifier"] = identifier
        return super().create(vals)

    @api.model
    def _get_identifier_values(self, vals):
        center = self.env["res.partner"].browse(vals.get("center_id", False))
        if not center or not center.encounter_sequence_id:
            raise ValidationError(_("Center and center sequence are required"))
        return center.encounter_sequence_id.with_context(
            sequence_tuple=True
        ).next_by_id()

    def get_next_number(self):
        self.ensure_one()
        return _update_nogap(self, 1)

    def get_next_number_cb(self, number_format):
        self.ensure_one()
        return number_format % self.get_next_number()
