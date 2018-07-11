import re
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
        inverse_name='encounter_id',
    )
    has_preinvoicing = fields.Boolean(
        compute='_compute_validation_values',
    )
    has_patient_invoice = fields.Boolean(
        compute='_compute_validation_values',
    )
    unauthorized_elements = fields.Boolean(
        compute='_compute_validation_values',
    )
    missing_authorization_number = fields.Boolean(
        compute='_compute_validation_values',
    )
    missing_subscriber_id = fields.Boolean(
        compute='_compute_validation_values',
    )

    @api.depends(
        'sale_order_ids.invoice_group_method_id',
        'sale_order_ids.coverage_agreement_id',
        'sale_order_ids.order_line.coverage_template_id.subscriber_required',
        'sale_order_ids.order_line.subscriber_id',
        'sale_order_ids.order_line.authorization_status',
    )
    def _compute_validation_values(self):
        preinvoicing = self.env.ref(
            'cb_medical_sale_invoice_group_method.by_preinvoicing')
        by_patient = self.env.ref(
            'cb_medical_sale_invoice_group_method.by_patient')
        for rec in self:
            rec.has_preinvoicing = bool(rec.sale_order_ids.filtered(
                lambda r: r.invoice_group_method_id == preinvoicing
            ))
            rec.has_patient_invoice = bool(rec.sale_order_ids.filtered(
                lambda r: r.invoice_group_method_id == by_patient
            ))
            rec.missing_subscriber_id = bool(
                rec.sale_order_ids.mapped('order_line').filtered(
                    lambda r: r.coverage_template_id.subscriber_required and
                    not re.match(
                        r.coverage_template_id.subscriber_format or '.+',
                        r.subscriber_id or '')
                )
            )
            rec.unauthorized_elements = bool(rec.sale_order_ids.filtered(
                lambda r: r.coverage_agreement_id
            ).mapped('order_line').filtered(
                lambda r: r.authorization_status != 'authorized'
            ))

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
