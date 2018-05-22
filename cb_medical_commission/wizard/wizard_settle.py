from odoo import api, fields, models, _
from datetime import date, timedelta


class SaleCommissionMakeSettle(models.TransientModel):
    _name = "sale.commission.no.invoice.make.settle"
    _inherit = "sale.commission.make.settle"

    @api.multi
    def action_settle(self):
        self.ensure_one()
        agent_line_obj = self.env['sale.order.line.agent']
        settlement_obj = self.env['sale.commission.settlement']
        settlement_line_obj = self.env['sale.commission.settlement.line']
        settlement_ids = []
        if not self.agents:
            self.agents = self.env['res.partner'].search(
                [('agent', '=', True)])
        date_to = fields.Date.from_string(self.date_to)
        for agent in self.agents:
            date_to_agent = self._get_period_start(agent, date_to)
            # Get non settled invoices
            agent_lines = agent_line_obj.search(
                [('date', '<', fields.Datetime.to_string(date_to_agent)),
                 ('agent', '=', agent.id),
                 ('settled', '=', False)], order='date')
            for company in agent_lines.mapped('company_id'):
                agent_lines_company = agent_lines.filtered(
                    lambda r: r.sale_line.order_id.company_id == company)
                if not agent_lines_company:
                    continue
                pos = 0
                sett_to = fields.Date.to_string(date(year=1900,
                                                     month=1,
                                                     day=1))
                while pos < len(agent_lines_company):
                    line = agent_lines_company[pos]
                    if line.date > sett_to:
                        sett_from = self._get_period_start(
                            agent, line.date)
                        sett_to = fields.Date.to_string(
                            self._get_next_period_date(
                                agent, sett_from) - timedelta(days=1))
                        sett_from = fields.Date.to_string(sett_from)
                        settlement = settlement_obj.search([
                            ('agent', '=', agent.id),
                            ('date_from', '=', sett_from),
                            ('date_to', '=', sett_to),
                            ('company_id', '=', company.id),
                            ('state', '=', 'settled')
                        ], limit=1)
                        if not settlement:
                            settlement = settlement_obj.create({
                                'agent': agent.id,
                                'date_from': sett_from,
                                'date_to': sett_to,
                                'company_id': company.id,
                            })
                        settlement_ids.append(settlement.id)
                    settlement_line_obj.create({
                        'settlement': settlement.id,
                        'agent_sale_line': [(6, 0, [line.id])],
                    })
                    pos += 1
        # go to results
        if len(settlement_ids):
            return {
                'name': _('Created Settlements'),
                'type': 'ir.actions.act_window',
                'views': [[False, 'list'], [False, 'form']],
                'res_model': 'sale.commission.settlement',
                'domain': [['id', 'in', settlement_ids]],
            }

        else:
            return {'type': 'ir.actions.act_window_close'}
