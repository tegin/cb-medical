# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MedicalProcedureRequest(models.Model):
    _inherit = 'medical.procedure.request'

    commission_agent_id = fields.Many2one(
        string='Commission Agent',
        comodel_name='res.partner',
    )
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

    @api.depends('service_id')
    def _compute_hide_fee(self):
        for rec in self:
            if self.service_id.medical_commission:
                rec.make_invisible = False
            else:
                rec.make_invisible = True

    def _get_procedure_values(self):
        res = super(MedicalProcedureRequest, self)._get_procedure_values()
        self.commission_agent_id = False
        valid_performer_ids = self.performer_id.commission_agent_ids
        if not valid_performer_ids:
            valid_performer_ids += self.performer_id
        if len(valid_performer_ids) == 1:
            self.commission_agent_id = valid_performer_ids[0]
        res.update({
            'commission_agent_id': self.commission_agent_id and
            self.commission_agent_id.id,
            'variable_fee': self.variable_fee,
            'fixed_fee': self.fixed_fee,
        })
        return res
