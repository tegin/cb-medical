from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MedicalGuard(models.Model):
    _name = "medical.guard"
    _description = "medical.guard"
    _inherit = ["medical.abstract", "mail.thread", "mail.activity.mixin"]

    date = fields.Datetime(
        required=True,
        track_visibility="onchange",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    delay = fields.Integer(
        required=True,
        track_visibility="onchange",
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
        track_visibility="onchange",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    location_id = fields.Many2one(
        "res.partner",
        domain=[("is_center", "=", True), ("guard_journal_id", "!=", False)],
        track_visibility="onchange",
        readonly=True,
        required=True,
        states={"draft": [("readonly", False)]},
    )
    product_id = fields.Many2one(
        "product.product",
        required=True,
        domain=[("type", "=", "service")],
        track_visibility="onchange",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    plan_guard_id = fields.Many2one("medical.guard.plan", readonly=True)
    invoice_line_ids = fields.One2many(
        "account.invoice.line", inverse_name="guard_id"
    )

    @api.model
    def _get_internal_identifier(self, vals):
        return self.env["ir.sequence"].next_by_code("medical.guard") or "/"

    def _complete_vals(self):
        return {"state": "completed"}

    @api.multi
    def complete(self):
        self.ensure_one()
        if not self.practitioner_id:
            raise ValidationError(_("Practitioner is required"))
        self.write(self._complete_vals())

    def _get_invoice_vals(self):
        journal = self.location_id.guard_journal_id
        invoice = self.env["account.invoice"].new(
            {
                "partner_id": self.practitioner_id.id,
                "type": (
                    "in_invoice" if journal.type == "purchase" else "in_refund"
                ),
                "journal_id": journal.id,
                "company_id": journal.company_id.id,
                "state": "draft",
            }
        )
        # Get other invoice values from onchanges
        invoice._onchange_partner_id()
        invoice._onchange_journal_id()
        return invoice._convert_to_write(invoice._cache)

    def _get_invoice_line_vals(self, invoice):
        invoice_line = self.env["account.invoice.line"].new(
            {
                "invoice_id": invoice.id,
                "product_id": self.product_id.id,
                "quantity": self.delay,
                "guard_id": self.id,
            }
        )
        # Get other invoice line values from product onchange
        invoice_line._onchange_product_id()
        invoice_line_vals = invoice_line._convert_to_write(invoice_line._cache)
        lang = self.env["res.lang"].search(
            [
                (
                    "code",
                    "=",
                    invoice.partner_id.lang
                    or self.env.context.get("lang", "en_US"),
                )
            ]
        )
        date = fields.Date.from_string(self.date)
        invoice_line_vals["name"] = _("%s at %s on %s") % (
            self.product_id.name,
            self.practitioner_id.name,
            date.strftime(lang.date_format),
        )
        return invoice_line_vals

    def get_invoice(self):
        journal = self.location_id.guard_journal_id
        partner = self.practitioner_id
        if partner.agent and partner.commission_agent_ids:
            partner = partner.commission_agent_ids[0]
        if self.practitioner_id.commission_agent_ids:
            partner = self.practitioner_id.commission_agent_ids[0]
        inv = self.env["account.invoice"].search(
            [
                ("partner_id", "=", partner.id),
                (
                    "type",
                    "=",
                    (
                        "in_invoice"
                        if journal.type == "purchase"
                        else "in_refund"
                    ),
                ),
                ("state", "=", "draft"),
                ("journal_id", "=", journal.id),
            ]
        )
        if not inv:
            inv = inv.create(self._get_invoice_vals())
        return inv

    def make_invoice(self):
        inv = self.get_invoice()
        self.env["account.invoice.line"].create(
            self._get_invoice_line_vals(inv)
        )
        inv.compute_taxes()
        return inv
