from itertools import groupby

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tests.common import Form


class MedicalGuard(models.Model):
    _name = "medical.guard"
    _description = "medical.guard"
    _inherit = ["medical.abstract", "mail.thread", "mail.activity.mixin"]
    _order = "date desc"

    date = fields.Datetime(
        required=True,
        tracking=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    delay = fields.Integer(
        required=True,
        tracking=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    state = fields.Selection(
        [("draft", "Draft"), ("completed", "Completed")],
        required=True,
        default="draft",
        readonly=True,
    )
    practitioner_id = fields.Many2one(
        "res.partner",
        domain=[("is_practitioner", "=", True)],
        tracking=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    location_id = fields.Many2one(
        "res.partner",
        domain=[("is_center", "=", True), ("guard_journal_id", "!=", False)],
        tracking=True,
        readonly=True,
        required=True,
        states={"draft": [("readonly", False)]},
    )
    product_id = fields.Many2one(
        "product.product",
        required=True,
        domain=[("type", "=", "service")],
        tracking=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    plan_guard_id = fields.Many2one("medical.guard.plan", readonly=True)
    invoice_line_ids = fields.One2many("account.move.line", inverse_name="guard_id")

    @api.depends("internal_identifier")
    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, record.internal_identifier))
        return result

    @api.model
    def _get_internal_identifier(self, vals):
        return self.env["ir.sequence"].next_by_code("medical.guard") or "/"

    def _complete_vals(self):
        return {"state": "completed"}

    def complete(self):
        self.ensure_one()
        if not self.practitioner_id:
            raise ValidationError(_("Practitioner is required"))
        self.write(self._complete_vals())

    def _prepare_invoice(self):
        journal = self[0].location_id.guard_journal_id
        move_type = "in_invoice" if journal.type == "purchase" else "in_refund"
        move_form = Form(
            self.env["account.move"]
            .with_company(journal.company_id.id)
            .with_context(
                default_move_type=move_type,
            )
        )
        partner = self._get_invoice_partner()
        move_form.partner_id = partner
        move_form.journal_id = journal
        for guard in self:
            with move_form.invoice_line_ids.new() as line_form:
                line_form.product_id = guard.product_id
                line_form.quantity = guard.delay
                # Put period string
                lang = self.env["res.lang"].search(
                    [
                        (
                            "code",
                            "=",
                            partner.lang or self.env.context.get("lang", "en_US"),
                        )
                    ]
                )
                line_form.name = _("%s at %s on %s") % (
                    guard.product_id.name,
                    guard.practitioner_id.name,
                    guard.date.strftime(lang.date_format),
                )
                line_form.guard_id = guard
        vals = move_form._values_to_save(all_fields=True)
        return vals

    def _get_invoice_grouping_keys(self):
        return ["practitioner_id", "location_id"]

    def _get_invoice_partner(self):
        agent = self[0].practitioner_id
        if agent.delegated_agent_id:
            return agent.delegated_agent_id
        return agent

    def make_invoice(self, grouped=True):
        invoice_vals_list = []
        medical_guard_obj = self.env[self._name]
        if grouped:
            invoice_grouping_keys = self._get_invoice_grouping_keys()
            medical_guards = groupby(
                self.sorted(
                    key=lambda x: [
                        x._fields[grouping_key].convert_to_write(x[grouping_key], x)
                        for grouping_key in invoice_grouping_keys
                    ],
                ),
                key=lambda x: [
                    x._fields[grouping_key].convert_to_write(x[grouping_key], x)
                    for grouping_key in invoice_grouping_keys
                ],
            )
            grouped_medical_guards = [
                medical_guard_obj.union(*list(sett))
                for _grouping_keys, sett in medical_guards
            ]
        else:
            grouped_medical_guards = self
        for medical_guard in grouped_medical_guards:
            invoice_vals = medical_guard._prepare_invoice()
            invoice_vals_list.append(invoice_vals)
        return self.env["account.move"].create(invoice_vals_list)
