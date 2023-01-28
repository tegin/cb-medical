from collections import defaultdict

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MedicalEncounter(models.Model):
    _inherit = "medical.encounter"

    sale_order_ids = fields.One2many(
        "sale.order", inverse_name="encounter_id", readonly=True
    )

    sale_order_count = fields.Integer(compute="_compute_sale_order_count")

    invoice_count = fields.Integer(compute="_compute_invoice_count")

    invoice_line_ids = fields.One2many(
        comodel_name="account.move.line",
        inverse_name="encounter_id",
        string="Invoice Lines",
    )

    @api.depends("sale_order_ids")
    def _compute_sale_order_count(self):
        for record in self:
            record.sale_order_count = len(record.sale_order_ids)

    @api.depends("invoice_line_ids")
    def _compute_invoice_count(self):
        for record in self:
            invoices = (
                self.env["account.move.line"]
                .search([("encounter_id", "=", record.id)])
                .mapped("move_id")
            )
            record.invoice_count = len(invoices)

    def _get_sale_order_vals(
        self,
        partner=False,
        coverage=False,
        agreement=False,
        third_party_partner=False,
        invoice_group_method=False,
        *kwargs
    ):
        vals = {
            "third_party_order": bool(third_party_partner),
            "third_party_partner_id": third_party_partner.id,
            "partner_id": partner.id,
            "encounter_id": self.id,
            "coverage_id": coverage.id,
            "patient_id": self.patient_id.id,
            "coverage_agreement_id": agreement.id,
            "pricelist_id": self.env.ref("product.list0").id,
            "patient_name": self.patient_id.display_name,
            "invoice_group_method_id": invoice_group_method.id,
        }
        if agreement:
            vals["company_id"] = agreement.company_id.id
        return vals

    def _generate_sale_order(
        self,
        order_lines,
        agreement=False,
        partner=False,
        coverage=False,
        third_party_partner=False,
        invoice_group_method=False,
        **kwargs
    ):
        is_third_party = bool(third_party_partner)
        order = self.sale_order_ids.filtered(
            lambda r: (
                (
                    agreement == r.coverage_agreement_id
                    and agreement
                    and r.coverage_id == coverage
                )
                or (not agreement and not r.coverage_agreement_id)
            )
            and (
                (
                    is_third_party
                    and r.third_party_order
                    and r.third_party_partner_id == third_party_partner
                )
                or (not is_third_party and not r.third_party_order)
            )
            and r.state == "draft"
            and r.partner_id == partner
            and r.invoice_group_method_id == invoice_group_method
        )
        if not order:
            vals = self._get_sale_order_vals(
                partner=partner,
                coverage=coverage,
                agreement=agreement,
                third_party_partner=third_party_partner,
                invoice_group_method=invoice_group_method,
                **kwargs,
            )
            order = (
                self.env["sale.order"].with_company(vals.get("company_id")).create(vals)
            )
            order.onchange_partner_id()
        order.ensure_one()
        order.with_company(order.company_id.id).write(
            {"order_line": [(0, 0, order_line) for order_line in order_lines]}
        )
        return order

    def get_patient_partner(self):
        return self.patient_id.partner_id

    def get_sale_order_lines(self):
        values = defaultdict(lambda: [])
        for careplan in self.careplan_ids:
            query = careplan.get_sale_order_query()
            for el in query:
                values[el[1:]].append(el[0])
        return values

    def _get_sale_order_parameters(self):
        return (
            "agreement",
            "partner",
            "coverage",
            "third_party_partner",
            "invoice_group_method",
        )

    def generate_sale_orders(self, values):
        params = self._get_sale_order_parameters()
        for vals in values:
            dict_vals = {}
            for i in range(0, len(vals)):
                dict_vals[params[i]] = vals[i]
            self._generate_sale_order(values[vals], **dict_vals)

    def create_sale_order(self):
        self.ensure_one()
        values = self.get_sale_order_lines()
        self.generate_sale_orders(values)
        return self.action_view_sale_order()

    def action_view_sale_order(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id("sale.action_orders")
        result = action.read()[0]
        result["domain"] = "[('encounter_id', '=', " + str(self.id) + ")]"
        if len(self.sale_order_ids) == 1:
            result["views"] = [(False, "form")]
            result["res_id"] = self.sale_order_ids.id
        return result

    @api.model
    def _create_encounter(
        self, patient=False, patient_vals=False, center=False, **kwargs
    ):
        encounter = super()._create_encounter(patient, patient_vals, center, **kwargs)
        careplan_data = kwargs.get("careplan_data") or []
        for careplan_vals in careplan_data:
            careplan_kwargs = kwargs.copy()
            careplan_kwargs.update(careplan_vals)
            encounter._add_careplan(**careplan_kwargs)
        return encounter

    # flake8: noqa: C901
    def _add_careplan(
        self,
        payor=False,
        sub_payor=False,
        coverage_template=False,
        subscriber_id=False,
        coverage=False,
        service=False,
        order_by=False,
        performer=False,
        authorization_number=False,
        qty=1,
        subscriber_magnetic_str=False,
        **kwargs
    ):
        if coverage:
            if isinstance(coverage, int):
                coverage = self.env["medical.coverage"].browse(coverage)
            if self.patient_id != coverage.patient_id:
                raise ValidationError(_("Patient must be the same"))
            if not payor:
                payor = coverage.coverage_template_id.payor_id
            if not coverage_template:
                coverage_template = coverage.coverage_template_id
        else:
            coverage = self.env["medical.coverage"]
        if not payor:
            raise ValidationError(_("Payor is required"))
        if isinstance(payor, int):
            payor = self.env["res.partner"].browse(payor)
        if not coverage_template:
            raise ValidationError(_("Coverage template is required"))
        if isinstance(coverage_template, int):
            coverage_template = self.env["medical.coverage.template"].browse(
                coverage_template
            )
        if not service:
            raise ValidationError(_("Service is required"))
        if isinstance(service, int):
            service = self.env["product.product"].browse(service)
        if not sub_payor:
            sub_payor = self.env["res.partner"]
        elif isinstance(sub_payor, int):
            sub_payor = self.env["res.partner"].browse(sub_payor)
        if not order_by:
            order_by = self.env["res.partner"]
        elif isinstance(order_by, int):
            order_by = self.env["res.partner"].browse(order_by)
        if not performer:
            performer = self.env["res.partner"]
        elif isinstance(performer, int):
            performer = self.env["res.partner"].browse(performer)
        self.ensure_one()
        careplan = (
            self.env["medical.encounter.add.careplan"]
            .with_context(default_encounter_id=self.id)
            .create(
                {
                    "payor_id": payor.id or coverage.payor_id.id or False,
                    "coverage_template_id": coverage_template.id or False,
                    "sub_payor_id": sub_payor.id or False,
                    "subscriber_id": subscriber_id,
                    "subscriber_magnetic_str": subscriber_magnetic_str,
                    "coverage_id": coverage.id or False,
                }
            )
            .with_context(
                default_order_by_id=order_by.id or False,
                default_service_id=service.id or False,
            )
            .run()
        )
        careplan._add_request_group(
            service=service,
            qty=qty,
            order_by=order_by,
            authorization_number=authorization_number,
            performer=performer,
            **kwargs,
        )
        return careplan

    def action_view_invoice(self):
        self.ensure_one()
        action = self.env.ref("account.action_move_out_invoice_type")
        result = action.read()[0]
        invoices = (
            self.env["account.move.line"]
            .search([("encounter_id", "=", self.id)])
            .mapped("move_id")
        )
        result["domain"] = [("id", "in", invoices.ids)]
        if len(invoices) == 1:
            res = self.env.ref("account.view_move_form")
            result["views"] = [(res and res.id or False, "form")]
            result["res_id"] = invoices.id
        return result
