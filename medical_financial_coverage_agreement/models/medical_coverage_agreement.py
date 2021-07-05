# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MedicalCoverageAgreement(models.Model):
    _name = "medical.coverage.agreement"
    _description = "Coverage Agreement"
    _inherit = ["medical.abstract", "mail.thread", "mail.activity.mixin"]

    def _get_default_currency_id(self):
        return self.env.user.company_id.currency_id.id

    name = fields.Char(string="Agreement Name", required=True, translate=True)
    active = fields.Boolean(default=True)
    center_ids = fields.Many2many(
        string="Centers",
        comodel_name="res.partner",
        domain=[("is_center", "=", True)],
        required=True,
        index=True,
        help="Medical centers",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        index=True,
        help="Responsible Medical Company",
    )
    coverage_template_ids = fields.Many2many(
        string="Coverage Templates",
        comodel_name="medical.coverage.template",
        relation="medical_coverage_agreement_medical_coverage_template_rel",
        column1="agreement_id",
        column2="coverage_template_id",
        help="Coverage templates related to this agreement",
        auto_join=True,
        copy=False,
    )
    nomenclature_id = fields.Many2one(
        "product.nomenclature", string="Printing nomenclature"
    )
    item_ids = fields.One2many(
        comodel_name="medical.coverage.agreement.item",
        inverse_name="coverage_agreement_id",
        string="Agreement items",
        ondelete="cascade",
        copy=True,
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Currency",
        default=_get_default_currency_id,
        required=True,
    )
    date_from = fields.Date("From", required=True, default=fields.Date.today())
    date_to = fields.Date("To")
    actual_date = fields.Date(default=fields.Date.today())
    principal_concept = fields.Selection(
        [("private", "Private"), ("coverage", "Coverage")], "Concept"
    )
    is_template = fields.Boolean(default=False, readonly=True)
    template_id = fields.Many2one(
        "medical.coverage.agreement",
        domain=[("is_template", "=", True)],
        readonly=True,
        tracking=True,
    )

    @api.constrains(
        "date_to", "date_from", "coverage_template_ids", "center_ids"
    )
    def _check_product_unicity(self):
        for rec in self:
            rec.item_ids._check_product()

    @api.constrains("is_template", "template_id", "coverage_template_ids")
    def _check_template(self):
        for rec in self:
            if not rec.is_template:
                continue
            if rec.coverage_template_ids:
                raise ValidationError(
                    _("Coverage cannot be defined on templates")
                )
            if rec.template_id:
                raise ValidationError(
                    _("Template cannot be defined on templates")
                )

    @api.model
    def _get_internal_identifier(self, vals):
        return (
            self.env["ir.sequence"].next_by_code("medical.coverage.agreement")
            or "/"
        )

    def toggle_active(self):
        res = super().toggle_active()
        for record in self.filtered(lambda r: not r.active):
            # Only set as unactive
            record.item_ids.write({"active": False})
        return res

    def action_search_item(self):
        action = self.env.ref(
            "medical_financial_coverage_agreement."
            "medical_coverage_agreement_item_action"
        )
        result = action.read()[0]
        result["context"] = {"default_coverage_agreement_id": self.id}
        result["domain"] = [("coverage_agreement_id", "=", self.id)]
        return result

    def set_template(self, template, set_items):
        self.ensure_one()
        self.write({"template_id": template.id})
        if not set_items:
            return
        for item in template.item_ids:
            if not self.item_ids.filtered(
                lambda r: r.product_id == item.product_id
            ):
                self.env["medical.coverage.agreement.item"].with_context(
                    default_coverage_agreement_id=self.id
                ).create(item._copy_agreement_vals(self))

    def _sort_data(self, data):
        result = []
        for d in data:
            item = {
                "product": d.product_id,
                "item": d,
                "nomenclature": self.env["product.nomenclature.product"],
            }
            if self.nomenclature_id:
                item["nomenclature"] = self.env[
                    "product.nomenclature.product"
                ].search(
                    [
                        ("nomenclature_id", "=", self.nomenclature_id.id),
                        ("product_id", "=", d.product_id.id),
                    ],
                    limit=1,
                )
            result.append(item)
        return sorted(
            result,
            key=lambda r: r["product"].default_code or r["product"].name,
        )

    def explore_child_data(self, childs, data):
        res = []
        if not childs:
            return res
        for child in childs.filtered(lambda r: r.id in data.keys()):
            res.append(
                {
                    "data": self._sort_data(data[child.id]),
                    "category": child,
                    "childs": self.explore_child_data(child.child_id, data),
                }
            )
        return sorted(res, key=lambda r: r["category"].name)

    def _agreement_report_domain(self, print_coverage):
        domain = [
            ("coverage_agreement_id", "=", self.id),
            ("total_price", ">", 0),
        ]
        if print_coverage:
            domain.append(("coverage_percentage", ">", 0))
        else:
            domain.append(("coverage_percentage", "<", 100))
        return domain

    def _agreement_report_data(self, print_coverage=True):
        self.ensure_one()
        data = {}
        sorted_data = []
        categs = self.env["product.category"]
        all_categs = self.env["product.category"]
        domain = self._agreement_report_domain(print_coverage)
        for item in self.env["medical.coverage.agreement.item"].search(domain):
            if item.categ_id.id not in data:
                categs |= item.categ_id
                data[item.categ_id.id] = self.env[
                    "medical.coverage.agreement.item"
                ]
            data[item.categ_id.id] |= item

        all_categs |= categs
        for categ in categs:
            ctg = categ
            while ctg.parent_id and ctg.parent_id not in all_categs:
                all_categs |= ctg.parent_id
                if ctg.parent_id not in data:
                    data[ctg.parent_id.id] = self.env[
                        "medical.coverage.agreement.item"
                    ]
                ctg = ctg.parent_id

        for categ in all_categs.filtered(lambda r: r.level == 0):
            sorted_data.append(
                {
                    "data": self._sort_data(data[categ.id]),
                    "category": categ,
                    "childs": self.explore_child_data(categ.child_id, data),
                }
            )
        return sorted(sorted_data, key=lambda r: r["category"].name)
