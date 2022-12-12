from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    related_patient_ids = fields.Many2many(
        "medical.patient",
        "medical_patient_invoicable_partner",
        "partner_id",
        "patient_id",
    )

    self_invoice_refund_sequence_id = fields.Many2one(
        comodel_name="ir.sequence",
        string="Self invoice refund sequence",
        ondelete="restrict",
    )

    def set_self_invoice(self):
        super().set_self_invoice()
        for record in self:
            if record.self_invoice_refund_sequence_id:
                continue
            if record.self_invoice:
                record.self_invoice_refund_sequence_id = (
                    self.env["ir.sequence"]
                    .sudo()
                    .create(
                        {
                            "name": record.name + " Self invoice refund sequence",
                            "implementation": "no_gap",
                            "number_increment": 1,
                            "padding": 4,
                            "prefix": self._self_invoice_refund_sequence_prefix(),
                            "use_date_range": True,
                            "number_next": 1,
                        }
                    )
                )

    def _self_invoice_sequence_prefix(self):
        return "CBINV/%(range_year)s/"

    def _self_invoice_refund_sequence_prefix(self):
        return "CBINV/R/%(range_year)s/"
