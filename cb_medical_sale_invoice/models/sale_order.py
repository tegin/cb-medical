from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    patient_name = fields.Char(
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}
    )

    @api.multi
    def _prepare_invoice(self):
        res = super()._prepare_invoice()
        if self.encounter_id:
            res['is_medical'] = True
            if self.coverage_agreement_id:
                p = self.coverage_id.coverage_template_id.payor_id
                res['show_patient'] = p.show_patient
                res['show_subscriber'] = p.show_subscriber
                res['show_authorization'] = p.show_authorization
        return res

    @api.multi
    @api.onchange('patient_name')
    def _onchange_patient_name(self):
        for rec in self:
            for line in rec.order_line.filtered(lambda r: r != rec):
                line.patient_name = rec.patient_name


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    authorization_number = fields.Char()
    subscriber_id = fields.Char()
    patient_name = fields.Char()

    @api.multi
    @api.onchange('patient_name')
    def _onchange_patient_name(self):
        for rec in self:
            rec.order_id.patient_name = rec.patient_name
            for line in rec.order_id.order_line.filtered(lambda r: r != rec):
                line.patient_name = rec.patient_name

    @api.multi
    def _prepare_invoice_line(self, qty):
        res = super()._prepare_invoice_line(qty)
        if self.encounter_id:
            res['patient_name'] = self.patient_name
            res['subscriber_id'] = self.subscriber_id
            res['encounter_id'] = self.encounter_id.id
            res['authorization_number'] = self.authorization_number
        return res
