from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    encounter_sequence_id = fields.Many2one(
        'ir.sequence',
        'Encounter sequence',
        readonly=True,
    )
    encounter_sequence_prefix = fields.Char(
        string="Prefix for Encounter sequence",
        help="Prefix used to generate the internal identifier of encounters",
    )
    center_alias = fields.Char()

    @api.model
    def _compute_encounter_prefix(self, prefix):
        return prefix

    @api.model
    def _prepare_ir_encounter_sequence(self, prefix):
        """Prepare the vals for creating the sequence
        :param prefix: a string with the prefix of the sequence.
        :return: a dict with the values.
        """
        vals = {
            "name": "Center " + prefix,
            "code": "res.partner.medical.center - " + prefix,
            "padding": 5,
            "prefix": self._compute_encounter_prefix(prefix),
            "company_id": False,
            "implementation": 'no_gap',
            "safe": True,
        }
        return vals

    @api.multi
    def write(self, vals):
        prefix = vals.get("encounter_sequence_prefix")
        if prefix:
            for rec in self:
                if rec.encounter_sequence_id:
                    rec.sudo().encounter_sequence_id.prefix = \
                        self._compute_encounter_prefix(prefix)
                else:
                    seq_vals = self._prepare_ir_encounter_sequence(prefix)
                    rec.encounter_sequence_id = self.env[
                        "ir.sequence"].create(seq_vals)
        return super().write(vals)

    @api.model
    def create(self, vals):
        prefix = vals.get("encounter_sequence_prefix")
        if prefix:
            seq_vals = self._prepare_ir_encounter_sequence(prefix)
            sequence = self.env["ir.sequence"].create(seq_vals)
            vals["encounter_sequence_id"] = sequence.id
        return super().create(vals)
