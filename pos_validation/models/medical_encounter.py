from odoo import api, fields, models


class MedicalEncounter(models.Model):
    _inherit = 'medical.encounter'

    validation_status = fields.Selection([
        ('none', 'None'),
        ('draft', 'Draft'),
        ('in_progress', 'In progress'),
        ('finished', 'Finished')
    ], default='none', required=True,
    )
    sale_order_line_ids = fields.One2many(
        'sale.order.line',
        related='sale_order_ids.order_line',
        readonly=True,
    )

    def onleave2finished_values(self):
        res = super().onleave2finished_values()
        res['validation_status'] = 'draft'
        return res

    @api.multi
    def close_view(self):
        return {'type': 'ir.actions.client', 'tag': 'history_back'}

    @api.multi
    def admin_validate(self):
        self.ensure_one()
        for sale_order in self.sale_order_ids.filtered(
            lambda r: r.coverage_agreement_id
        ):
            sale_order.action_confirm()
        # We assume that private SO are already confirmed
        by_patient = self.env.ref(
            'cb_medical_sale_invoice_group_method.by_patient')
        for sale_order in self.sale_order_ids.filtered(
            lambda r: r.invoice_group_method_id == by_patient
        ):
            self.create_invoice(sale_order)
        self.write({'validation_status': 'finished'})
        if not self.pos_session_id.encounter_ids.filtered(
            lambda r: r.validation_status == 'in_progress'
        ):
            self.pos_session_id.action_validation_finish()
        return self.close_view()

    def create_invoice(self, sale_order):
        """Hook in order to add more functionality (automatic printing)"""
        invoice = self.env['account.invoice'].browse(
            sale_order.action_invoice_create())
        invoice.action_invoice_open()
        return invoice
