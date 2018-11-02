from odoo import api, fields, models


class SalerOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_private = fields.Boolean(
        compute='_compute_is_private'
    )
    pos_session_id = fields.Many2one(
        comodel_name='pos.session',
        string='PoS Session',
        store=True,
        compute='_compute_pos_session',
        readonly=1,
    )
    coverage_agreement_id = fields.Many2one(
        'medical.coverage.agreement',
        related='order_id.coverage_agreement_id',
        readonly=True,
    )
    coverage_agreement_item_id = fields.Many2one(
        'medical.coverage.agreement.item',
        readonly=True,
    )
    authorization_format_id = fields.Many2one(
        'medical.authorization.format',
        related='coverage_agreement_item_id.authorization_format_id',
        readonly=True,
    )
    coverage_template_id = fields.Many2one(
        'medical.coverage.template',
        related='order_id.coverage_template_id',
        readonly=True,
    )
    payor_id = fields.Many2one(
        'res.partner',
        related='order_id.coverage_template_id.payor_id',
        readonly=True,
    )
    authorization_number = fields.Char(readonly=True)

    @api.depends('order_id.coverage_agreement_id')
    def _compute_is_private(self):
        for record in self:
            record.is_private = not bool(record.order_id.coverage_agreement_id)

    @api.depends('order_id.is_down_payment', 'order_id.pos_session_id')
    def _compute_pos_session(self):
        for record in self.filtered(lambda r: not r.order_id.is_down_payment):
            record.pos_session_id = record.order_id.pos_session_id

    @api.depends('state', 'product_uom_qty', 'qty_delivered', 'qty_to_invoice',
                 'qty_invoiced', 'order_id.third_party_order',
                 'order_id.encounter_id.validation_status',
                 'order_id.coverage_agreement_id')
    def _compute_invoice_status(self):
        res = super()._compute_invoice_status()
        for line in self.filtered(
            lambda r:
                r.order_id.coverage_agreement_id and
                r.order_id.encounter_id.validation_status != 'finished'
        ):
            # We cannot invoice a sale order if we have not validated the so.
            line.invoice_status = 'no'
        return res

    @api.multi
    def check_authorization_action(self):
        self.ensure_one()
        group = False
        if self.request_group_id:
            group = self.request_group_id
        elif self.procedure_request_id:
            group = self.procedure_request_id.request_group_id
        elif self.medication_request_id:
            group = self.medication_request_id.request_group_id
        elif self.document_reference_id:
            group = self.document_reference_id.request_group_id
        elif self.laboratory_request_id:
            group = self.laboratory_request_id.request_group_id
        elif self.laboratory_event_id:
            group = self.laboratory_event_id.laboratory_request_id.\
                request_group_id
        return group.check_authorization_action()
