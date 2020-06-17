from itertools import groupby
from odoo import api, fields, models, _


class MedicalQuote(models.Model):
    _name = "medical.quote"
    _description = "Medical Quote"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "quote_date desc, id desc"

    name = fields.Char(default=lambda self: _("New"))
    is_private = fields.Boolean("Is private")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("sent", "Sent"),
            ("confirm", "Confirmed"),
            ("cancel", "Cancelled"),
        ],
        string="Status",
        default="draft",
        required=True,
        track_visibility="always",
    )
    quote_date = fields.Date(
        "Date",
        default=fields.Date.context_today,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    validity_date = fields.Date(
        "Expiry Date", readonly=True, states={"draft": [("readonly", False)]}
    )
    confirmation_date = fields.Date("Confirmation Date", readonly=True)
    user_id = fields.Many2one(
        "res.users",
        string="Salesperson",
        readonly=True,
        states={"draft": [("readonly", False)]},
        default=lambda self: self.env.user,
    )
    company_id = fields.Many2one(
        "res.company",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        default=lambda self: self.env.user.company_id,
    )
    patient_id = fields.Many2one(
        "medical.patient",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    patient_name = fields.Char("Patient name")
    payor_id = fields.Many2one(
        "res.partner",
        "Payor",
        required=True,
        domain=[("is_payor", "=", True)],
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    coverage_template_id = fields.Many2one(
        "medical.coverage.template",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    center_id = fields.Many2one(
        "res.partner",
        domain=[("is_center", "=", True)],
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    quote_line_ids = fields.One2many(
        comodel_name="medical.quote.line",
        inverse_name="quote_id",
        string="Quote Lines",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )

    origin_agreement_id = fields.Many2one(
        "medical.coverage.agreement", readonly=True
    )

    agreement_ids = fields.Many2many(
        "medical.coverage.agreement", compute="_compute_agreements", store=True
    )
    add_agreement_line_id = fields.Many2one(
        "medical.coverage.agreement.item",
        string="Add service",
        domain="[('coverage_agreement_id', 'in', agreement_ids),"
        "('plan_definition_id', '!=', False)]",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    add_quantity = fields.Float(
        "Add Quantity",
        readonly=True,
        states={"draft": [("readonly", False)]},
        default=1,
    )
    amount = fields.Float("Amount", compute="_compute_amount", store=True)
    currency_id = fields.Many2one(
        "res.currency", readonly=True, related="company_id.currency_id"
    )
    note = fields.Text(
        "Terms and conditions",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )

    comment_template1_id = fields.Many2one(
        "base.comment.template", string="Top Comment Template"
    )
    comment_template2_id = fields.Many2one(
        "base.comment.template", string="Bottom Comment Template"
    )
    note1 = fields.Html("Top Comment")
    note2 = fields.Html("Bottom Comment")

    @api.onchange("comment_template1_id")
    def _set_note1(self):
        comment = self.comment_template1_id
        if comment:
            self.note1 = comment.get_value()

    @api.onchange("comment_template2_id")
    def _set_note2(self):
        comment = self.comment_template2_id
        if comment:
            self.note2 = comment.get_value()

    @api.model
    def _get_agreements_domain(self):
        return [
            ("center_ids", "=", self.center_id.id),
            ("coverage_template_ids", "=", self.coverage_template_id.id),
            "|",
            ("date_from", "=", False),
            ("date_from", "<=", self.quote_date),
            "|",
            ("date_to", "=", False),
            ("date_to", ">=", self.quote_date),
        ]

    @api.depends("coverage_template_id", "center_id", "quote_date")
    def _compute_agreements(self):
        for rec in self:
            domain = rec._get_agreements_domain()
            rec.agreement_ids = self.env["medical.coverage.agreement"].search(
                domain
            )

    @api.depends(
        "quote_line_ids", "quote_line_ids.price", "quote_line_ids.quantity"
    )
    def _compute_amount(self):
        for quote in self:
            quote.amount = sum(quote.quote_line_ids.mapped("amount"))

    @api.onchange("patient_id")
    def _onchange_patient_id(self):
        if self.patient_id:
            self.patient_name = self.patient_id.name
            templates = self.patient_id.coverage_ids.mapped(
                "coverage_template_id"
            )
            payors = self.patient_id.coverage_ids.mapped(
                "coverage_template_id.payor_id"
            )
            if self.coverage_template_id not in templates:
                self.coverage_template_id = False
            if templates:
                self.coverage_template_id = templates[0]
            if self.payor_id not in payors:
                self.payor_id = False
            if payors:
                self.payor_id = payors[0]
        else:
            return {"domain": {"coverage_template_id": [], "payor_id": []}}

    @api.onchange("payor_id")
    def _onchange_payor_id(self):
        if self.payor_id:
            templates = self.payor_id.coverage_template_ids
            if self.coverage_template_id not in templates:
                self.coverage_template_id = False
            if len(templates) == 1:
                self.coverage_template_id = templates[0]
            return {
                "domain": {
                    "coverage_template_id": [("id", "in", templates.ids)]
                }
            }
        else:
            return {"domain": {"coverage_template_id": []}}

    @api.onchange("add_agreement_line_id")
    def _onchange_add_agreement_line_id(self):
        if self.add_agreement_line_id:
            self.add_quantity = 1.0

    @api.onchange("coverage_template_id")
    def _onchange_coverage_template_id(self):
        if self.coverage_template_id:
            self.payor_id = self.coverage_template_id.payor_id
        else:
            return {"domain": {"payor_id": [("is_payor", "=", True)]}}

    @api.model
    def _search_agreement_items(self):
        items = []
        agreement = self.add_agreement_line_id
        if (
            agreement.plan_definition_id
            and agreement.plan_definition_id.is_billable
        ):
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
                    agreement = self.env[
                        "medical.coverage.agreement.item"
                    ].get_item(
                        service, self.coverage_template_id, self.center_id
                    )
                    items.append([agreement, qty])

        return items

    @api.model
    def _prepare_medical_quote_line(self, item, cat):
        coverage_price = (
            item[0].coverage_percentage * item[0].total_price
        ) / 100
        private_price = (
            (100 - item[0].coverage_percentage) * item[0].total_price
        ) / 100
        price = private_price if self.is_private else coverage_price
        return {
            "agreement_line_id": item[0].id,
            "plan_definition_id": item[0].plan_definition_id.id,
            "layout_category_id": cat.id,
            "product_id": item[0].product_id.id,
            "quantity": item[1] * self.add_quantity,
            "description": item[0].product_id.description_quote,
            "price": price,
            "coverage_agreement_id": item[0].coverage_agreement_id.id,
        }

    @api.multi
    def button_send(self):
        for rec in self:
            rec.state = "sent"

    @api.multi
    def button_confirm(self):
        for rec in self:
            rec.state = "confirm"
            rec.confirmation_date = fields.Date.today()

    @api.multi
    def button_cancel(self):
        for rec in self:
            rec.state = "cancel"

    @api.multi
    def button_draft(self):
        for rec in self:
            rec.state = "draft"

    @api.multi
    def _prepare_medical_quote_layout_category(self):
        self.ensure_one()
        return {
            "name": self.add_agreement_line_id.product_id.name,
            "quote_id": self.id,
        }

    @api.multi
    def button_add_line(self):
        self.ensure_one()
        items = self._search_agreement_items()
        cat = self.env["medical.quote.layout_category"]
        if len(items) > 1:
            cat = self.env["medical.quote.layout_category"].search(
                [
                    ("quote_id", "=", self.id),
                    ("name", "=", self.add_agreement_line_id.product_id.name),
                ],
                limit=1,
            )
            if not cat:
                data = self._prepare_medical_quote_layout_category()
                cat = (
                    self.env["medical.quote.layout_category"]
                    .sudo()
                    .create(data)
                )
        for item in items:
            medical_quote_line_data = self._prepare_medical_quote_line(
                item, cat
            )
            self.quote_line_ids += self.env["medical.quote.line"].new(
                medical_quote_line_data
            )
        self.add_agreement_line_id = False
        self.add_quantity = 1

    def _get_name(self, vals):
        if "company_id" in vals:
            name = self.env["ir.sequence"].with_context(
                force_company=vals["company_id"]
            ).next_by_code("medical.quote") or _("New")
        else:
            name = self.env["ir.sequence"].next_by_code("medical.quote") or _(
                "New"
            )
        return name

    @api.model
    def create(self, vals):
        if vals.get("name", "/") == "/":
            vals["name"] = self._get_name(vals)
        return super(MedicalQuote, self).create(vals)

    @api.multi
    def lines_layouted(self):
        """
        Returns the lines classified by sale_layout_category and separated in
        pages according to the category pagebreaks. Used to render the report.
        """
        self.ensure_one()
        report_pages = [[]]
        for category, lines in groupby(
            self.quote_line_ids, lambda l: l.layout_category_id
        ):
            # If last added category induced a pagebreak,
            # this one will be on a new page
            if report_pages[-1] and report_pages[-1][-1]["pagebreak"]:
                report_pages.append([])
            # Append category to current report page
            report_pages[-1].append(
                {
                    "name": category and category.name or False,
                    "subtotal": category and category.subtotal,
                    "pagebreak": category and category.pagebreak,
                    "lines": list(lines),
                }
            )

        return report_pages


class MedicalQuoteLine(models.Model):
    _name = "medical.quote.line"
    _description = "Medical Quote Line"
    _order = "quote_id, layout_category_id, sequence, id"

    quote_id = fields.Many2one(
        "medical.quote", "Medical Quote", required=True, ondelete="cascade"
    )
    sequence = fields.Integer(default=10)
    agreement_line_id = fields.Many2one(
        "medical.coverage.agreement.item", readonly=True
    )
    plan_definition_id = fields.Many2one(
        string="Plan definition",
        comodel_name="workflow.plan.definition",
        readonly=True,
    )
    product_tmpl_id = fields.Many2one(
        "product.template",
        related="product_id.product_tmpl_id",
        readonly=True,
        store=True,
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Service",
        ondelete="restrict",
        domain=[("type", "=", "service"), ("sale_ok", "=", True)],
        required=True,
        readonly=True,
    )
    description = fields.Text()
    quantity = fields.Float("Quantity")
    categ_id = fields.Many2one(
        comodel_name="product.category",
        string="Category",
        ondelete="restrict",
        related="product_id.categ_id",
        store=True,
        readonly=True,
    )
    coverage_agreement_id = fields.Many2one(
        comodel_name="medical.coverage.agreement",
        string="Medical agreement",
        index=True,
        ondelete="cascade",
        readonly=True,
    )
    template_id = fields.Many2one(
        "medical.coverage.agreement",
        readonly=True,
        related="coverage_agreement_id.template_id",
    )
    currency_id = fields.Many2one(
        related="coverage_agreement_id.currency_id", readonly=True
    )
    company_id = fields.Many2one(
        "res.company",
        "Company",
        readonly=True,
        related="quote_id.company_id",
        store=True,
    )
    is_private = fields.Boolean(related="quote_id.is_private", readonly=True)
    price = fields.Float(string="Price")
    amount = fields.Float(
        string="Amount", compute="_compute_amount", readonly=True
    )
    layout_category_id = fields.Many2one(
        "medical.quote.layout_category", string="Section"
    )
    layout_category_sequence = fields.Integer(string="Layout Sequence")

    @api.multi
    @api.depends("price", "quantity")
    def _compute_amount(self):
        for rec in self:
            rec.amount = rec.price * rec.quantity
