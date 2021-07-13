# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    session_sequence_id = fields.Many2one(
        'ir.sequence',
        'Sequence for sessions'
    )
    session_sequence_prefix = fields.Char()
    requires_approval = fields.Boolean(default=True)

    @api.model
    def _compute_session_prefix(self, prefix):
        return prefix

    @api.model
    def _prepare_ir_session_sequence(self, prefix):
        """Prepare the vals for creating the sequence
        :param prefix: a string with the prefix of the sequence.
        :return: a dict with the values.
        """
        vals = {
            "name": "Pos Config " + prefix,
            "code": "pos.config - " + prefix,
            "padding": 5,
            "prefix": self._compute_session_prefix(prefix),
            "company_id": False,
            "implementation": 'no_gap'
        }
        return vals

    @api.multi
    def write(self, vals):
        prefix = vals.get("session_sequence_prefix", False)
        if prefix:
            for rec in self:
                if rec.session_sequence_id:
                    rec.sudo().session_sequence_id.prefix = \
                        self._compute_session_prefix(prefix)
                else:
                    rec.session_sequence_id = self.env[
                        "ir.sequence"
                    ].create(
                        self._prepare_ir_session_sequence(prefix))
        return super().write(vals)
