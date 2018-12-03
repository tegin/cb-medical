# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class MedicalRequest(models.AbstractModel):
    _inherit = 'medical.request'

    sale_order_line_ids = fields.One2many(
        string='Sale order lines',
        comodel_name='sale.order.line',
        compute='_compute_sale_order_line_ids',
    )
    is_sellable_insurance = fields.Boolean(
        compute='_compute_is_sellable',
    )
    is_sellable_private = fields.Boolean(
        compute='_compute_is_sellable',
    )
    sub_payor_id = fields.Many2one(
        'res.partner',
        domain="[('payor_id', '=', payor_id), ('is_sub_payor', '=', True)]"
    )
    payor_id = fields.Many2one(
        'res.partner',
        related='coverage_id.coverage_template_id.payor_id',
        readonly=True,
    )
    authorization_method_id = fields.Many2one(
        'medical.authorization.method',
        track_visibility=True,
        readonly=True,
    )
    invoice_group_method_id = fields.Many2one(
        'invoice.group.method',
        string='Invoice Group Method',
        track_visibility=True,
        readonly=True,
    )

    def get_third_party_partner(self):
        return False

    def _compute_sale_order_line_ids(self):
        inverse_field_name = self._get_parent_field_name()
        for rec in self:
            rec.sale_order_line_ids = self.env['sale.order.line'].search(
                [(inverse_field_name, '=', rec.id)])

    @api.onchange('coverage_id')
    def _onchange_coverage_id(self):
        for record in self:
            record.sub_payor_id = False

    @api.depends('is_billable', 'sale_order_line_ids',
                 'coverage_agreement_item_id', 'state')
    def _compute_is_sellable(self):
        for rec in self:
            ca = rec.coverage_agreement_id
            rec.is_sellable_private = bool(
                rec.state not in ['cancelled'] and
                rec.is_billable and
                len(rec.sale_order_line_ids.filtered(
                    lambda r: (
                        r.state != 'cancel' and
                        not r.order_id.coverage_agreement_id)
                )) == 0 and
                (rec.coverage_agreement_item_id.private_price > 0)
            )
            rec.is_sellable_insurance = bool(
                rec.state not in ['cancelled'] and
                rec.is_billable and
                len(rec.sale_order_line_ids.filtered(
                    lambda r: (
                        r.state != 'cancel' and
                        r.order_id.coverage_agreement_id.id == ca.id)
                )) == 0 and
                rec.coverage_agreement_item_id.coverage_price > 0
            )

    def compute_price(self, is_insurance):
        cai = self.coverage_agreement_item_id
        return cai.coverage_price if is_insurance else cai.private_price

    def get_sale_order_line_vals(self, is_insurance):
        res = {
            'product_id': self.service_id.id,
            'name': self.service_id.name or self.name,
            self._get_parent_field_name(): self.id,
            'product_uom_qty': 1,
            'product_uom': self.service_id.uom_id.id,
            'price_unit': self.compute_price(is_insurance),
            'authorization_status': self.authorization_status,
            'encounter_id': self.encounter_id.id or False,
        }
        if is_insurance:
            res['invoice_group_method_id'] = self.invoice_group_method_id.id
        return res

    def check_is_billable(self):
        if self.is_billable:
            return True
        # Agreement is researched if it is not billable
        self.coverage_agreement_item_id = self.env[
            'medical.coverage.agreement.item'
        ].search([
            (
                'coverage_template_ids', '=',
                self.coverage_id.coverage_template_id.id),
            ('product_id', '=', self.service_id.id)
        ], limit=1)
        if not self.coverage_agreement_item_id:
            raise ValidationError(_('Agreement must be defined'))
        return self.is_billable

    @api.multi
    def breakdown(self):
        self.ensure_one()
        if not self.is_billable or not self.is_breakdown:
            raise ValidationError(_('Cannot breakdown a not billable line'))
        if self.sale_order_line_ids:
            raise ValidationError(_(
                'Sale order is created. '
                'It must be deleted in order to breakdown'))
        self.is_billable = False
        self.is_breakdown = False
        for model in self._get_request_models():
            requests = self.env[model].search([
                ('parent_model', '=', self._name),
                ('parent_id', '=', self.id)
            ])
            for request in requests:
                if not request.check_is_billable():
                    request.is_billable = True

    @api.multi
    def get_sale_order_query(self):
        query = []
        fieldname = self._get_parent_field_name()
        request_models = self._get_request_models()
        for request in self:
            if request.is_sellable_insurance:
                query.append((
                    request.coverage_agreement_id.id,
                    request.careplan_id.get_payor(),
                    request.coverage_id.id,
                    True,
                    request.get_third_party_partner()
                    if request.third_party_bill else 0,
                    request
                ))
            if request.is_sellable_private:
                query.append((
                    0,
                    request.encounter_id.get_patient_partner(),
                    False,
                    False,
                    request.get_third_party_partner()
                    if request.third_party_bill else 0,
                    request
                ))
            for model in request_models:
                childs = self.env[model].search([
                    (fieldname, '=', request.id),
                    ('parent_id', '=', request.id),
                    ('parent_model', '=', request._name),
                    ('state', '!=', 'cancelled')
                    ])
                query += childs.get_sale_order_query()
        return query

    def _update_related_activity(self, vals, parent, plan, action):
        #TODO: Review
        pass
