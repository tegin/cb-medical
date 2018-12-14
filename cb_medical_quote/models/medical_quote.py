from odoo import api, fields, models, _


class MedicalQuote(models.Model):
    _name = 'medical.quote'
    _description = 'Medical Quote'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'quote_date desc, id desc'

    name = fields.Char(default=lambda self: _('New'),
                       )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('sent', 'Sent'),
         ('confirm', 'Confirmed'),
         ('cancel', 'Cancelled')],
        string='Status', default='draft', required=True,
        track_visibility='always',
    )
    quote_date = fields.Date('Date', default=fields.Date.context_today,
                             readonly=True,
                             states={'draft': [('readonly', False)]},
                             )
    validity_date = fields.Date('Expiry Date',
                                readonly=True,
                                states={'draft': [('readonly', False)]},
                                )
    confirmation_date = fields.Date('Confirmation Date', readonly=True,)
    user_id = fields.Many2one('res.users',
                              string='Salesperson',
                              readonly=True,
                              states={'draft': [('readonly', False)]},
                              default=lambda self: self.env.user,
                              )
    company_id = fields.Many2one('res.company', required=True,
                                 readonly=True,
                                 states={'draft': [('readonly', False)]},
                                 default=lambda self: self.env.user.company_id,
                                 )
    patient_id = fields.Many2one('medical.patient',
                                 readonly=True,
                                 states={'draft': [('readonly', False)]},
                                 )
    payor_id = fields.Many2one('res.partner', 'Payor', required=True,
                               domain="[('is_payor', '=', True)]",
                               readonly=True,
                               states={'draft': [('readonly', False)]},
                               )
    coverage_template_id = fields.Many2one('medical.coverage.template',
                                           required=True,
                                           readonly=True,
                                           states={
                                               'draft': [('readonly', False)]},
                                           )
    center_id = fields.Many2one(
        'res.partner',
        domain=[('is_center', '=', True)],
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    quote_line_ids = fields.One2many(
        comodel_name='medical.quote.line', inverse_name='quote_id',
        string='Quote Lines',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    agreement_ids = fields.Many2many('medical.coverage.agreement',
                                     compute='_compute_agreements',
                                     )
    add_agreement_line_id = fields.Many2one(
        'medical.coverage.agreement.item',
        string='Add service',
        domain="[('coverage_agreement_id', 'in', agreement_ids),"
               "('plan_definition_id', '!=', False)]",
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    add_quantity = fields.Float('Add Quantity',
                                readonly=True,
                                states={'draft': [('readonly', False)]},
                                )
    total_amount = fields.Float(
        'Total Amount', compute='_compute_amount', store=True)
    private_amount = fields.Float(
        'Private Amount', compute='_compute_amount', store=True)
    coverage_amount = fields.Float(
        'Coverage Amount', compute='_compute_amount', store=True)
    currency_id = fields.Many2one('res.currency',
                                  related='company_id.currency_id')
    note = fields.Text('Terms and conditions',
                       readonly=True,
                       states={'draft': [('readonly', False)]},
                       )

    @api.model
    def _get_agreements_domain(self):
        return [
            ('center_ids', '=', self.center_id.id),
            ('coverage_template_ids', '=', self.coverage_template_id.id),
            '|', ('date_from', '=', False),
            ('date_from', '<=', self.quote_date),
            '|', ('date_to', '=', False),
            ('date_to', '>=', self.quote_date)
        ]

    @api.depends('coverage_template_id', 'center_id')
    def _compute_agreements(self):
        for rec in self:
            domain = rec._get_agreements_domain()
            rec.agreement_ids = self.env['medical.coverage.agreement'].search(
                domain)

    @api.depends('quote_line_ids', 'quote_line_ids.total_price',
                 'quote_line_ids.quantity',
                 'quote_line_ids.coverage_percentage')
    def _compute_amount(self):
        for quote in self:
            quote.private_amount = sum(self.quote_line_ids.mapped(
                'private_amount'))
            quote.coverage_amount = sum(self.quote_line_ids.mapped(
                'coverage_amount'))
            quote.total_amount = sum(self.quote_line_ids.mapped(
                'total_amount'))

    @api.onchange('patient_id')
    def _onchange_patient_id(self):
        if self.patient_id:
            templates = self.patient_id.coverage_ids.mapped(
                'coverage_template_id')
            payors = self.patient_id.coverage_ids.mapped(
                'coverage_template_id.payor_id')
            if self.coverage_template_id not in templates:
                self.coverage_template_id = False
            if templates:
                self.coverage_template_id = templates[0]
            if self.payor_id not in payors:
                self.payor_id = False
            if payors:
                self.payor_id = payors[0]
            return {'domain': {
                'coverage_template_id': [('id', 'in', templates.ids)],
                'payor_id': [('id', 'in', payors.ids)]}
                }
        else:
            return {'domain': {
                'coverage_template_id': [],
                'payor_id': []}
            }

    @api.onchange('payor_id')
    def _onchange_payor_id(self):
        if self.payor_id:
            templates = self.payor_id.coverage_template_ids
            if self.coverage_template_id not in templates:
                self.coverage_template_id = False
            if len(templates) == 1:
                self.coverage_template_id = templates[0]
            return {'domain': {
                'coverage_template_id': [('id', 'in', templates.ids)]}
                }
        else:
            return {'domain': {
                'coverage_template_id': []}
            }

    @api.onchange('add_agreement_line_id')
    def _onchange_add_agreement_line_id(self):
        if self.add_agreement_line_id:
            self.add_quantity = 1.0

    @api.onchange('coverage_template_id')
    def _onchange_coverage_template_id(self):
        if self.coverage_template_id:
            self.payor_id = self.coverage_template_id.payor_id
        else:
            return {'domain': {
                'payor_id': []}
            }

    @api.model
    def _search_agreement_items(self):
        items = []
        agreement = self.add_agreement_line_id
        if agreement.plan_definition_id and \
                agreement.plan_definition_id.is_billable:
            items.append([agreement, 1])
            return items
        # If there's a plan definition, look for actions
        plan = agreement.plan_definition_id
        if plan:
            for action in plan.direct_action_ids:
                if action.is_billable:
                    activity = action.activity_definition_id
                    service = activity and activity.service_id
                    qty = activity.quantity
                    agreement = \
                        self.env['medical.coverage.agreement.item'].get_item(
                            service, self.coverage_template_id)
                    items.append([agreement, qty])

        return items

    @api.model
    def _prepare_medical_quote_line(self, item):
        return {
            'agreement_line_id': item[0].id,
            'plan_definition_id': item[0].plan_definition_id.id,
            'product_id': item[0].product_id.id,
            'quantity': item[1] * self.add_quantity,
            'total_price': item[0].total_price,
            'coverage_percentage': item[0].coverage_percentage,
            'coverage_agreement_id': item[0].coverage_agreement_id.id,
        }

    @api.multi
    def button_send(self):
        for rec in self:
            rec.state = 'sent'

    @api.multi
    def button_confirm(self):
        for rec in self:
            rec.state = 'confirm'
            rec.confirmation_date = fields.Date.today()

    @api.multi
    def button_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    @api.multi
    def button_draft(self):
        for rec in self:
            rec.state = 'draft'

    @api.multi
    def button_add_line(self):
        self.ensure_one()
        items = self._search_agreement_items()
        for item in items:
            medical_quote_line_data = self._prepare_medical_quote_line(item)
            self.quote_line_ids += self.env['medical.quote.line'].new(
                medical_quote_line_data)
        self.add_agreement_line_id = False
        self.add_quantity = False

    def _get_name(self, vals):
        if 'company_id' in vals:
            name = self.env['ir.sequence'].with_context(
                force_company=vals['company_id']).next_by_code(
                'medical.quote') or _('New')
        else:
            name = self.env['ir.sequence'].next_by_code(
                'medical.quote') or _('New')
        return name

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self._get_name(vals)
        return super(MedicalQuote, self).create(vals)


class MedicalQuoteLine(models.Model):
    _name = 'medical.quote.line'
    _description = 'Medical Quote Line'

    quote_id = fields.Many2one('medical.quote', 'Medical Quote',
                               required=True, ondelete='cascade',
                               )
    sequence = fields.Integer(default=10)
    agreement_line_id = fields.Many2one(
        'medical.coverage.agreement.item', readonly=True)
    plan_definition_id = fields.Many2one(
        string='Plan definition',
        comodel_name='workflow.plan.definition',
        readonly=True,
    )
    product_tmpl_id = fields.Many2one(
        'product.template',
        related='product_id.product_tmpl_id',
        readonly=True,
        store=True,
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Service',
        ondelete='restrict',
        domain=[('type', '=', 'service'), ('sale_ok', '=', True)],
        required=True,
        readonly=True,
    )
    quantity = fields.Float('Quantity')
    categ_id = fields.Many2one(
        comodel_name='product.category',
        string='Category',
        ondelete='restrict',
        related='product_id.categ_id',
        store=True,
        readonly=True,
    )
    total_price = fields.Float(
        string='Total price',
        required=True,
        readonly=True,
    )
    coverage_percentage = fields.Float(
        string='Coverage %', readonly=True,
    )
    coverage_agreement_id = fields.Many2one(
        comodel_name='medical.coverage.agreement',
        string='Medical agreement',
        index=True,
        ondelete='cascade',
        readonly=True,
    )
    template_id = fields.Many2one(
        'medical.coverage.agreement', readonly=True,
        related='coverage_agreement_id.template_id',
    )
    currency_id = fields.Many2one(
        related='coverage_agreement_id.currency_id',
        readonly=True,
    )
    company_id = fields.Many2one(
        'res.company',
        'Company',
        readonly=True,
        related='quote_id.company_id',
        store=True,
    )
    coverage_price = fields.Float(
        string='Coverage price',
        compute='_compute_amount',
        store=True,
        readonly=True,
    )
    private_price = fields.Float(
        string='Private price',
        compute='_compute_amount',
        store=True,
        readonly=True,
    )
    coverage_amount = fields.Float(
        string='Coverage amount',
        compute='_compute_amount',
        store=True,
        readonly=True,
    )
    private_amount = fields.Float(
        string='Private amount',
        compute='_compute_amount',
        store=True,
        readonly=True,
    )
    total_amount = fields.Float(
        string='Total amount',
        compute='_compute_amount',
        store=True,
        readonly=True,
    )

    @api.multi
    @api.depends('total_price', 'quantity', 'coverage_percentage')
    def _compute_amount(self):
        for rec in self:
            rec.coverage_price = \
                ((rec.coverage_percentage * rec.total_price) / 100)
            rec.coverage_amount = rec.coverage_price * rec.quantity
            rec.private_price = \
                ((100 - rec.coverage_percentage) * rec.total_price) / 100
            rec.private_amount = rec.private_price * rec.quantity
            rec.total_amount = rec.private_amount + rec.coverage_amount
