# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv import expression
from odoo.tools import float_compare


class MedicalCoverageAgreementItem(models.Model):
    _name = "medical.coverage.agreement.item"
    _description = "Medical Coverage Agreement Item"
    _rec_name = "product_id"

    def _default_coverage_percentage(self):
        agreement_id = self.env.context.get("default_coverage_agreement_id", False)
        agreement = self.env["medical.coverage.agreement"].browse(agreement_id)
        if agreement:
            if agreement.principal_concept == "coverage":
                return 100.0
            else:
                return 0.0

    plan_definition_id = fields.Many2one(
        string="Plan definition", comodel_name="workflow.plan.definition"
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
        auto_join=True,  # In order to improve search time
    )

    item_comment = fields.Text(string="Comment")

    default_code = fields.Char(
        related="product_id.default_code",
        string="Internal Reference",
        readonly=True,
    )

    categ_id = fields.Many2one(
        comodel_name="product.category",
        string="Category",
        ondelete="restrict",
        related="product_id.categ_id",
        store=True,
        readonly=True,
    )
    total_price = fields.Float(string="Total price", required=True)
    coverage_percentage = fields.Float(
        string="Coverage %",
        required=True,
        default=_default_coverage_percentage,
    )
    coverage_agreement_id = fields.Many2one(
        comodel_name="medical.coverage.agreement",
        string="Medical agreement",
        index=True,
        ondelete="cascade",
        auto_join=True,
        copy=False,
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
        related="coverage_agreement_id.company_id",
        store=True,
    )
    coverage_price = fields.Float(string="Coverage price", compute="_compute_price")
    private_price = fields.Float(string="Private price", compute="_compute_price")
    private_sellable = fields.Float(
        string="Sellable to private", compute="_compute_price"
    )
    coverage_sellable = fields.Float(
        string="Sellable to coverage", compute="_compute_price"
    )
    active = fields.Boolean(default=True)

    @api.onchange("product_id")
    def _onchange_product(self):
        related = self.template_id.item_ids.filtered(
            lambda r: r.product_id == self.product_id
        )
        if related:
            self._update_by_related(related)
        self.item_comment = (
            self.product_id.agreement_comment if self.product_id else False
        )

    def _update_by_related(self, related):
        rounding = self.currency_id.rounding
        if not self.plan_definition_id:
            self.plan_definition_id = related.plan_definition_id
        if not float_compare(self.total_price, 0, precision_rounding=rounding):
            self.total_price = related.total_price

    @api.depends("total_price", "coverage_percentage")
    def _compute_price(self):
        for rec in self:
            rec.coverage_price = (rec.coverage_percentage * rec.total_price) / 100
            rec.private_price = (
                (100 - rec.coverage_percentage) * rec.total_price
            ) / 100
            rec.private_sellable = rec.private_price > 0 or (
                rec.coverage_percentage < 100 and rec.product_tmpl_id.include_zero_sales
            )
            rec.coverage_sellable = rec.coverage_price > 0 or (
                rec.coverage_percentage > 0 and rec.product_tmpl_id.include_zero_sales
            )

    @api.constrains("product_id", "coverage_agreement_id", "active")
    def _check_product(self):
        for rec in self.filtered(lambda r: r.active):
            if self.search(
                [
                    ("id", "!=", rec.id),
                    (
                        "coverage_agreement_id",
                        "=",
                        rec.coverage_agreement_id.id,
                    ),
                    ("product_id", "=", rec.product_id.id),
                    ("active", "=", True),
                ],
                limit=1,
            ):
                raise ValidationError(_("Product must be unique for an agreement"))
            aggr = rec.coverage_agreement_id
            domain = [
                ("product_id", "=", rec.product_id.id),
                ("coverage_agreement_id", "!=", aggr.id),
                (
                    "coverage_agreement_id.center_ids",
                    "in",
                    aggr.center_ids.ids,
                ),
                (
                    "coverage_agreement_id.coverage_template_ids",
                    "in",
                    aggr.coverage_template_ids.ids,
                ),
                "|",
                ("coverage_agreement_id.date_to", "=", False),
                ("coverage_agreement_id.date_to", ">=", aggr.date_from),
            ]
            if aggr.date_to:
                domain += [("coverage_agreement_id.date_from", "<=", aggr.date_to)]
            repeated = self.search(domain, limit=1)
            if repeated:
                raise ValidationError(
                    _(
                        "One of this actions cannot be completed:\n- If you are "
                        "trying to add an agreement to a coverage template then "
                        "this agreement can't be added as it contains one or more "
                        "products that already exist in another agreement "
                        "belonging to this Coverage Template.\n"
                        "- If you are trying to add a new product to an Agreement "
                        "that means there is a coverage template that "
                        "already has this product in another Agreement.\n\n"
                        "Conflictive agreement: [%s] %s\n"
                        "Conflictive product: %s"
                    )
                    % (
                        repeated.coverage_agreement_id.internal_identifier,
                        repeated.coverage_agreement_id.display_name,
                        repeated.product_id.name,
                    )
                )

    def _copy_agreement_vals(self, agreement):
        return {
            "coverage_agreement_id": agreement.id,
            "plan_definition_id": self.plan_definition_id.id or False,
            "product_id": self.product_id.id,
            "total_price": self.total_price,
        }

    @api.model
    def _name_search(
        self,
        name="",
        args=None,
        operator="ilike",
        limit=100,
        name_get_uid=None,
    ):
        """search full name and barcode"""
        args = args or []
        domain = []
        if name:
            domain = [
                "|",
                ("product_id.name", operator, name),
                ("product_id.default_code", operator, name),
            ]
        return self._search(
            expression.AND([domain, args]),
            limit=limit,
            access_rights_uid=name_get_uid,
        )
