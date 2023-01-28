# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models


class SalePreinvoiceGroup(models.Model):
    _name = "sale.preinvoice.group"
    _description = "Sale Preinvoice Group"
    _inherit = ["medical.abstract", "mail.thread", "mail.activity.mixin"]
    _rec_name = "internal_identifier"

    agreement_id = fields.Many2one(
        comodel_name="medical.coverage.agreement",
        string="Agreement",
        required=False,
        readonly=True,
    )
    coverage_template_id = fields.Many2one("medical.coverage.template", readonly=True)
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        readonly=True,
    )
    move_id = fields.Many2one("account.move", "Invoice", readonly=True)
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
        required=True,
        readonly=True,
    )
    partner_invoice_id = fields.Many2one(
        comodel_name="res.partner",
        string="Invoice Partner",
        required=True,
        readonly=True,
    )
    line_ids = fields.One2many(
        string="Lines",
        comodel_name="sale.order.line",
        inverse_name="preinvoice_group_id",
    )
    validated_line_ids = fields.One2many(
        string="Validated lines",
        comodel_name="sale.order.line",
        compute="_compute_lines",
    )
    non_validated_line_ids = fields.One2many(
        string="Non validated lines",
        comodel_name="sale.order.line",
        compute="_compute_lines",
    )
    invoice_group_method_id = fields.Many2one(
        string="Invoice Group Method",
        comodel_name="invoice.group.method",
        tracking=True,
    )
    state = fields.Selection(
        string="Status",
        required="True",
        selection=[
            ("draft", "Draft"),
            ("in_progress", "In progress"),
            ("validation", "Pending validation"),
            ("closed", "Closed"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        help="Current state of the pre-invoice group.",
    )
    current_sequence = fields.Integer(default=1)

    @api.model
    def _get_internal_identifier(self, vals):
        return self.env["ir.sequence"].next_by_code("medical.preinvoice.group") or "/"

    @api.depends("line_ids")
    def _compute_lines(self):
        for record in self:
            record.validated_line_ids = record.line_ids.filtered(
                lambda r: r.is_validated
            )
            record.non_validated_line_ids = record.line_ids.filtered(
                lambda r: not r.is_validated
            )

    def validate_line(self, line):
        if not line.is_validated:
            line.write({"is_validated": True, "sequence": self.get_sequence()})
        self._compute_lines()

    def invalidate_line(self, line):
        if line.is_validated:
            line.write({"is_validated": False, "sequence": 999999})
        self._compute_lines()

    def get_sequence(self):
        val = self.current_sequence + 1
        self.write({"current_sequence": val})
        return val

    def invoice_domain(self):
        partner_id = self.partner_id.id
        if self.partner_invoice_id:
            partner_id = self.partner_invoice_id.id
        return [
            ("move_type", "=", "out_invoice"),
            ("invoice_group_method_id", "=", self.invoice_group_method_id.id),
            ("partner_id", "=", partner_id),
            ("agreement_id", "=", self.agreement_id.id or False),
            ("company_id", "=", self.company_id.id),
            ("state", "=", "draft"),
            (
                "coverage_template_id",
                "=",
                self.coverage_template_id.id or False,
            ),
        ]

    def create_invoice_values(self):
        inv_data = self.validated_line_ids[0].order_id._prepare_invoice()
        inv_data["agreement_id"] = self.agreement_id.id or False
        inv_data["ref"] = self.internal_identifier
        journal = self.invoice_group_method_id.get_journal(self.company_id)
        if journal:
            inv_data["journal_id"] = journal.id
        return inv_data

    def close(self):
        self.ensure_one()
        for line in self.non_validated_line_ids:
            line.preinvoice_group_id = False
        if self.validated_line_ids and not self.invoice_group_method_id.no_invoice:
            self.move_id = self.env["account.move"].search(
                self.invoice_domain(), limit=1
            )
            if not self.move_id:
                self.move_id = (
                    self.env["account.move"]
                    .with_context(mail_auto_subscribe_no_notify=True)
                    .create(self.create_invoice_values())
                )
            else:
                self.move_id.write(
                    {"ref": ",".join([self.move_id.ref, self.internal_identifier])}
                )
            seq = len(self.move_id.invoice_line_ids) + 1
            data = []
            for line in self.validated_line_ids:
                # TODO: Do this in batch, it will be faster...
                line.write({"sequence": seq})
                seq += 1
                data.append((0, 0, line._prepare_invoice_line()))
            self.move_id.write({"invoice_line_ids": data})
        self.write({"state": "closed"})

    def start(self):
        self.ensure_one()
        self.write({"state": "in_progress"})

    def close_sorting(self):
        self.ensure_one()
        self.write({"state": "validation"})

    def cancel(self):
        self.ensure_one()
        for line in self.line_ids:
            line.preinvoice_group_id = False
        self.write({"state": "cancelled"})

    def _show_lines(self, encounter, processed_lines):
        show_lines = (
            _("The following lines have been processed from " "Encounter %s:\n")
            % encounter.display_name
        )
        for line in processed_lines:
            show_lines = "{} {} [{}]\n".format(
                show_lines,
                line.product_id.name,
                line.order_id.name,
            )
        return show_lines + _(
            "Scan the next barcode or press Close to " "finish scanning."
        )

    def scan_barcode_preinvoice(self, barcode):
        encounter_id = self.env["medical.encounter"].search(
            [("internal_identifier", "=", barcode)]
        )
        if not encounter_id:
            status = (
                _(
                    "Barcode %s does not correspond to any "
                    "Encounter. Try with another barcode or "
                    "press Close to finish scanning."
                )
                % barcode
            )
            status_state = "warning"
        else:
            processed_lines = self.line_ids.filtered(
                lambda r: r.encounter_id.id == encounter_id.id and not r.is_validated
            )
            if not processed_lines:
                status = (
                    _(
                        "The Encounter %s does not belong to this pre-invoice "
                        "group. Try with another barcode or press Close to finish "
                        "scanning."
                    )
                    % encounter_id.display_name
                )
                status_state = "warning"
            else:
                for line in processed_lines:
                    self.validate_line(line)
                status = self._show_lines(encounter_id, processed_lines)
                status_state = "waiting"
                self._compute_lines()
        result = self.env["ir.actions.act_window"]._for_xml_id(
            "barcode_action.barcode_action_action"
        )
        result["context"] = {
            "default_model": self._name,
            "default_method": "scan_barcode_preinvoice",
            "default_res_id": self.id,
            "default_status": status,
            "default_state": status_state,
        }
        return result
