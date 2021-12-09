from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SalerOrderLine(models.Model):
    _inherit = "sale.order.line"

    is_private = fields.Boolean(compute="_compute_is_private")
    pos_session_id = fields.Many2one(
        comodel_name="pos.session",
        string="PoS Session",
        store=True,
        compute="_compute_pos_session",
        readonly=1,
    )
    validation_status = fields.Selection(
        related="encounter_id.validation_status", readonly=True
    )
    coverage_agreement_id = fields.Many2one(
        "medical.coverage.agreement",
        related="order_id.coverage_agreement_id",
        readonly=True,
    )
    coverage_agreement_item_id = fields.Many2one(
        "medical.coverage.agreement.item", readonly=True
    )
    authorization_format_id = fields.Many2one(
        "medical.authorization.format",
        related="coverage_agreement_item_id.authorization_format_id",
        readonly=True,
    )
    coverage_template_id = fields.Many2one(
        "medical.coverage.template",
        related="order_id.coverage_template_id",
        readonly=True,
    )
    subscriber_information = fields.Char(
        readonly=True,
        related="order_id.coverage_template_id.subscriber_information",
    )
    payor_id = fields.Many2one(
        "res.partner",
        related="order_id.coverage_template_id.payor_id",
        readonly=True,
    )
    authorization_number = fields.Char(readonly=True)
    invoiced_agent_ids = fields.Many2many(
        "account.invoice.line.agent", compute="_compute_invoiced_agent_ids"
    )

    @api.depends("medical_model", "medical_res_id")
    def _compute_invoiced_agent_ids(self):
        for record in self:
            invoiced_agent_ids = self.env["account.invoice.line.agent"]
            if record.medical_model:
                request = self.env[record.medical_model].browse(
                    record.medical_res_id
                )
                lab_req = request.mapped("laboratory_request_ids")
                invoiced_agent_ids = (
                    request.mapped(
                        "procedure_request_ids.procedure_ids.invoice_agent_ids"
                    )
                    | lab_req.mapped("invoice_agent_ids")
                    | lab_req.mapped("laboratory_event_ids.invoice_agent_ids")
                )
            record.invoiced_agent_ids = invoiced_agent_ids

    @api.depends("order_id.coverage_agreement_id")
    def _compute_is_private(self):
        for record in self:
            record.is_private = not bool(record.order_id.coverage_agreement_id)

    @api.depends("order_id.is_down_payment", "order_id.pos_session_id")
    def _compute_pos_session(self):
        for record in self.filtered(lambda r: not r.order_id.is_down_payment):
            record.pos_session_id = record.order_id.pos_session_id

    @api.depends(
        "state",
        "product_uom_qty",
        "qty_delivered",
        "qty_to_invoice",
        "qty_invoiced",
        "order_id.third_party_order",
        "order_id.encounter_id.validation_status",
        "order_id.coverage_agreement_id",
    )
    def _compute_invoice_status(self):
        res = super()._compute_invoice_status()
        for line in self.filtered(
            lambda r: r.order_id.coverage_agreement_id
            and r.order_id.encounter_id.validation_status != "finished"
        ):
            # We cannot invoice a sale order if we have not validated the so.
            line.invoice_status = "no"
        return res

    def check_authorization_action(self):
        self.ensure_one()
        request = self.env[self.medical_model].browse(self.medical_res_id)
        if request._name == "medical.request.group":
            pass
        elif request._name == "medical.laboratory.event":
            request = request.laboratory_request_id.request_group_id
        else:
            request = request.request_group_id
        return request.check_authorization_action()

    def medical_cancel(self, cancel_reason):
        if not self.env.user.has_group(
            "pos_validation.group_medical_encounter_validation"
        ):
            raise UserError(
                _("This can only be executed if you can validate encounters")
            )
        for rec in self:
            if rec.order_id.state != "draft":
                raise UserError(
                    _("Only on draft orders you can cancel an element")
                )
            request = False
            if rec.medical_model:
                request = (
                    self.env[rec.medical_model]
                    .browse(rec.medical_res_id)
                    .exists()
                )
            if not request:
                raise UserError(_("This is not a medical line"))
            request.with_context(
                cancel_reason_id=cancel_reason.id,
                cancel_reason=cancel_reason.name,
                validation_cancel=True,
            ).cancel()

    def change_plan(self, service):
        self.ensure_one()
        if self.order_id.state != "draft":
            raise UserError(
                _("Change of plan can only be applied to draft orders")
            )
        request = (
            self.env[self.medical_model].browse(self.medical_res_id).exists()
        )
        if not request:
            raise UserError(
                _("Change of plan can only be applied to request groups")
            )
        request.with_context(validation_change=True).change_plan_definition(
            self.env["medical.coverage.agreement.item"].get_item(
                service, request.coverage_template_id, request.center_id
            )
        )
