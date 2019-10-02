from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    patient_name = fields.Char(
        states={"draft": [("readonly", False)], "sent": [("readonly", False)]}
    )
    subscriber_id = fields.Char(
        states={"draft": [("readonly", False)], "sent": [("readonly", False)]}
    )

    @api.multi
    def _prepare_invoice(self):
        res = super()._prepare_invoice()
        if self.encounter_id:
            res["is_medical"] = True
            if self.coverage_agreement_id:
                p = self.coverage_id.coverage_template_id
                res["show_patient"] = p.payor_id.show_patient
                res["show_subscriber"] = p.payor_id.show_subscriber
                res["show_authorization"] = p.payor_id.show_authorization
                res["coverage_template_id"] = p.id
            else:
                res["encounter_id"] = self.encounter_id.id
        return res

    @api.model
    def sale_shared_fields(self):
        return ["patient_name", "subscriber_id"]

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        if not self.env.context.get("not_sale_share_values", False):
            shared_vals = {}
            for key in self.sale_shared_fields():
                if key in vals:
                    shared_vals.update({key: vals[key]})
            if shared_vals:
                self.mapped("order_line").with_context(
                    not_sale_share_values=True
                ).write(shared_vals)
        return res


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    authorization_number = fields.Char()
    subscriber_id = fields.Char()
    patient_name = fields.Char()

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        if not self.env.context.get("not_sale_share_values", False):
            shared_vals = {}
            for key in self.env["sale.order"].sale_shared_fields():
                if key in vals:
                    shared_vals.update({key: vals[key]})
            if shared_vals:
                self.mapped("order_id").with_context(
                    not_sale_share_values=True
                ).write(shared_vals)
                self.mapped("order_id").mapped("order_line").filtered(
                    lambda r: r not in self
                ).with_context(not_sale_share_values=True).write(shared_vals)
        return res

    @api.multi
    def _prepare_invoice_line(self, qty):
        res = super()._prepare_invoice_line(qty)
        if self.encounter_id:
            res["patient_name"] = self.patient_name
            res["subscriber_id"] = self.subscriber_id
            res["encounter_id"] = self.encounter_id.id
            res["authorization_number"] = self.authorization_number
            agreement = self.order_id.coverage_agreement_id
            if agreement:
                if agreement.file_reference:
                    res["facturae_file_reference"] = agreement.file_reference
                if agreement.discount and agreement.discount > 0.0:
                    res["discount"] = agreement.discount
        if self.coverage_template_id:
            nomenc = self.coverage_template_id.payor_id.invoice_nomenclature_id
            if nomenc:
                item = nomenc.item_ids.filtered(
                    lambda r: r.product_id == self.product_id
                )
                if item:
                    res["name"] = item.name
        return res

    def _prepare_third_party_order_line(self):
        res = super()._prepare_third_party_order_line()
        res["authorization_number"] = self.authorization_number or False
        res["subscriber_id"] = self.subscriber_id or False
        res["patient_name"] = self.patient_name or False
        return res
