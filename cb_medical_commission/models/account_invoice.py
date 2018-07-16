# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.model
    def _prepare_line_agents_data(self, line):
        if line.sale_line_ids and line.encounter_id:
            sale_line = line.sale_line_ids[0]
            procedures = sale_line.procedure_ids
            res = []
            for procedure in procedures:
                res.append({
                    'agent': procedure.commission_agent_id.id,
                    'commission': procedure.commission_agent_id.commission.id,
                    'procedure_id': procedure.id,
                })
            return res
        return super()._prepare_line_agents_data(line)


class AccountInvoiceLineAgent(models.Model):
    _inherit = 'account.invoice.line.agent'

    procedure_id = fields.Many2one(
        'medical.procedure',
        readonly=True,
    )

    _sql_constraints = [
        ('unique_agent',
         'UNIQUE(invoice_line, agent, parent_agent_line_id, procedure_id, is_cancel)',
         'You can only add one time each agent.')
    ]

    def get_commission_cancel_vals(self, agent=False):
        res = super().get_commission_cancel_vals(agent)
        res['procedure_id'] = self.procedure_id.id or False
        return res
