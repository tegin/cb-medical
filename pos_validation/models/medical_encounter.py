import re
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class MedicalEncounter(models.Model):
    _inherit = 'medical.encounter'

    validation_status = fields.Selection([
        ('none', 'None'),
        ('draft', 'Draft'),
        ('in_progress', 'In progress'),
        ('finished', 'Finished')
    ], default='none', readonly=True, track_visibility=True,)
    sale_order_line_ids = fields.One2many(
        'sale.order.line',
        inverse_name='encounter_id',
    )
    has_preinvoicing = fields.Boolean(
        compute='_compute_validation_values',
    )
    is_preinvoiced = fields.Boolean(
        default=False, track_visibility=True,
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
    missing_practitioner = fields.Boolean(
        compute='_compute_validation_values',
    )

    @api.depends(
        'sale_order_ids.order_line.invoice_group_method_id',
        'sale_order_ids.coverage_agreement_id',
        'sale_order_ids.order_line.coverage_template_id.subscriber_required',
        'sale_order_ids.order_line.subscriber_id',
        'sale_order_ids.order_line.authorization_number',
        'sale_order_ids.order_line.authorization_format_id',
        'sale_order_ids.order_line.authorization_method_id',
        'sale_order_ids.order_line.authorization_status',
    )
    def _compute_validation_values(self):
        for rec in self:
            lines = rec.sale_order_ids.filtered(
                lambda r: r.coverage_agreement_id
            ).mapped('order_line')
            rec.has_preinvoicing = bool(lines.filtered(
                lambda r: r.invoice_group_method_id.invoice_by_preinvoice
            ))
            rec.has_patient_invoice = bool(lines.filtered(
                lambda r: r.invoice_group_method_id.invoice_at_validation
            ))
            rec.missing_subscriber_id = bool(lines.filtered(
                lambda r:
                    r.coverage_template_id.subscriber_required and
                    not re.match(
                        r.coverage_template_id.subscriber_format or '.+',
                        r.subscriber_id or ''
                    )))
            rec.unauthorized_elements = bool(lines.filtered(
                lambda r: r.authorization_status != 'authorized'))
            rec.missing_authorization_number = bool(lines.filtered(
                lambda r:
                r.authorization_format_id and
                r.authorization_method_id and
                r.authorization_method_id.authorization_required and
                not r.authorization_format_id.check_value(
                    r.authorization_number
                )
            ))
            rec.missing_practitioner = bool(rec.sale_order_ids.mapped(
                'order_line.procedure_ids'
            ).filtered(lambda r: (
                r.procedure_service_id.medical_commission
                and not r.performer_id
                and r.state not in ['aborted']
            )))

    def onleave2finished_values(self):
        res = super().onleave2finished_values()
        res['validation_status'] = 'draft'
        return res

    @api.multi
    def close_view(self):
        actions = [{'type': 'ir.actions.client', 'tag': 'history_back'}]
        if self.env.context.get('from_barcode_reader', False):
            action = self.env.ref(
                'barcode_action.barcode_action_action')
            result = action.read()[0]
            result['context'] = {
                'default_model': 'pos.session',
                'default_res_id': self.pos_session_id.id,
                'default_method': 'open_validation_encounter'
            }
            actions.append(result)
        return {'type': 'ir.actions.act_multi', 'actions': actions}

    def toggle_is_preinvoiced(self):
        for record in self:
            record.is_preinvoiced = not record.is_preinvoiced

    def check_validation(self):
        if self.has_preinvoicing and not self.is_preinvoiced:
            raise ValidationError(_('You must check the documentation.'))
        if self.unauthorized_elements:
            raise ValidationError(_('Some elements are not authorized'))
        if self.missing_authorization_number:
            raise ValidationError(_(
                'There is missing authorization numbers. Fill them first.'))
        if self.missing_subscriber_id:
            raise ValidationError(_(
                'The subscriber id is required'
            ))
        if self.missing_practitioner:
            raise ValidationError(_(
                'The performer is required in at least a procedure'
            ))

    def _admin_validation_values(self):
        return {'validation_status': 'finished'}

    @api.multi
    def admin_validate(self):
        self.ensure_one()
        self.check_validation()
        for sale_order in self.sale_order_ids.filtered(
            lambda r: r.coverage_agreement_id
        ):
            sale_order.with_context(
                no_third_party_number=True
            ).action_confirm()
            # We assume that private SO are already confirmed
            self.create_invoice(sale_order)
        # Third party orders should be confirmed
        for sale_order in self.sale_order_ids.filtered(
            lambda r: r.third_party_order
        ).mapped('third_party_order_ids'):
            sale_order.with_context(
                no_third_party_number=True
            ).action_confirm()
        self.write(self._admin_validation_values())
        if not self.pos_session_id.encounter_ids.filtered(
            lambda r: r.validation_status not in 'finished'
        ):
            self.pos_session_id.action_validation_finish()
        return self.close_view()

    def create_invoice(self, sale_order):
        """Hook in order to add more functionality"""
        invoices = self.env['account.invoice']
        for group in sale_order.order_line.mapped(
            'invoice_group_method_id'
        ).filtered(lambda r: r.invoice_at_validation):
            invoice = self.env['account.invoice'].browse(
                sale_order.with_context(
                    invoice_group_method_id=group.id,
                ).action_invoice_create())
            self.post_process_invoice(invoice, group)
            invoice.action_invoice_open()
            invoices |= invoice
        return invoices

    def post_process_invoice(self, invoice, group):
        pass
