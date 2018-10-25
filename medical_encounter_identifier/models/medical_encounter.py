from odoo import api, fields, models, _
from odoo.addons.base.ir.ir_sequence import _update_nogap
from odoo.exceptions import ValidationError


class MedicalEncounter(models.Model):
    _inherit = 'medical.encounter'

    center_id = fields.Many2one(
        'res.partner',
        domain=[('is_center', '=', True)],
        required=True,
        track_visibility=True,
    )
    location_id = fields.Many2one(
        required=False, default=False, invisible=1
    )

    internal_identifier_prefix = fields.Char(readonly=True)
    internal_identifier_value = fields.Integer(default=0, readonly=True)
    internal_identifier_suffix = fields.Char(readonly=True)
    internal_identifier_dc = fields.Char(readonly=True)

    number_next = fields.Integer(default=1)
    # We must keep this name in order to use _update_nogap function

    @api.model
    def create(self, vals):
        if vals.get('internal_identifier_value', 0) == 0:
            pf, val, suf, dc, identifier = self._get_internal_identifier_values(
                vals)
            vals['internal_identifier_prefix'] = pf
            vals['internal_identifier_value'] = val
            vals['internal_identifier_suffix'] = suf
            vals['internal_identifier_dc'] = dc
            vals['internal_identifier'] = identifier
        return super().create(vals)

    @api.model
    def _get_internal_identifier_values(self, vals):
        center = self.env['res.partner'].browse(
            vals.get('center_id', False))
        if not center or not center.encounter_sequence_id:
            raise ValidationError(_('Center and center sequence are required'))
        return center.encounter_sequence_id.with_context(
            sequence_tuple=True).next_by_id()

    @api.multi
    def get_next_number(self):
        self.ensure_one()
        return _update_nogap(self, 1)

    @api.multi
    def get_next_number_cb(self, format):
        self.ensure_one()
        return format % self.get_next_number()
