# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MedicalProcedure(models.Model):
    _inherit = 'medical.procedure'

    variable_fee = fields.Float(
        string='Variable fee (%)',
        default='0.0',
    )
    fixed_fee = fields.Float(
        string='Fixed fee',
        default='0.0',
    )
    make_invisible = fields.Boolean(
        default=True,
        compute='_compute_hide_fee',
    )
    commission_agent_id = fields.Many2one(
        string='Commission Agent',
        comodel_name='res.partner',
    )

    @api.onchange('performer_id')
    def _onchange_performer_id(self):
        valid_performer_ids = self.performer_id.commission_agent_ids
        if not valid_performer_ids:
            valid_performer_ids += self.performer_id
        if len(valid_performer_ids) == 1:
            self.commission_agent_id = valid_performer_ids[0]
        else:
            return {
                'domain':
                    {'commission_agent_id':
                        [('id', 'in',
                          self.performer_id.commission_agent_ids.ids)]
                     }
            }

    @api.depends('service_id')
    def _compute_hide_fee(self):
        for rec in self:
            if self.service_id.medical_commission:
                rec.make_invisible = False
            else:
                rec.make_invisible = True
