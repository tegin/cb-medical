# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MgmtsystemNonconformity(models.Model):

    _inherit = 'mgmtsystem.nonconformity'

    encounter_id = fields.Many2one('medical.encounter')

    ref = fields.Char(readonly=True, copy=False, default='/')

    @api.model
    def create(self, vals):
        if vals.get('ref', '/') == '/':
            sequence = self.env.ref(
                'mgmtsystem_nonconformity.seq_mgmtsystem_nonconformity'
            )
            vals['ref'] = sequence.next_by_id()
        return super().create(vals)
