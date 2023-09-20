from odoo import _, api, models
from odoo.exceptions import ValidationError
from odoo.tests.common import Form
from odoo.tools.float_utils import float_compare


class MedicalEncounter(models.Model):
    _inherit = "medical.encounter"

    def _change_invoice_partner(self, partner):
        self.ensure_one()
        partner.ensure_one()
        partner.write({"related_patient_ids": [(4, self.patient_id.id)]})
        so = self.sale_order_ids.filtered(
            lambda r: not r.coverage_agreement_id and not r.is_down_payment
        )
        invoices = so.mapped("invoice_ids")
        sos = self.sale_order_ids.filtered(
            lambda r: r.third_party_order and not r.coverage_agreement_id
        )
        final_inv = invoices.filtered(lambda r: r.encounter_final_invoice)
        final_sos = sos.filtered(lambda r: r.encounter_final_sale_order)
        inv_res = self.env["account.move"]
        sos_res = self.env["sale.order"]
        if not final_inv:
            final_inv = invoices
        if not final_sos:
            final_sos = sos
        if final_inv and final_inv.partner_id != partner:
            invoice_new_partner = Form(
                self.env["account.move"]
                .with_company(final_inv.company_id.id)
                .with_context(
                    default_move_type="out_invoice",
                    default_invoice_origin=final_inv.name,
                    default_ref=_("New partner of: %s, %s")
                    % (final_inv.name, _("Change invoice partner")),
                )
            )
            invoice_new_partner.journal_id = final_inv.journal_id
            invoice_new_partner.currency_id = final_inv.currency_id
            invoice_new_partner.partner_id = partner
            invoice_new_partner = invoice_new_partner.save()
            invoice_line_vals = []
            for il in final_inv.invoice_line_ids.filtered(
                lambda r: not r.down_payment_line_id
            ):
                default_data = {
                    "move_id": False,
                    "sale_line_ids": [(4, id) for id in il.sale_line_ids.ids],
                }
                # This should never happen, but we leave it JIC.
                if il.move_id.move_type == "out_refund":
                    default_data["quantity"] = -1 * il.quantity
                invoice_line_vals.append((0, 0, il.copy_data(default=default_data)[0]))
            invoice_new_partner.write(
                {
                    "invoice_line_ids": invoice_line_vals,
                    "encounter_final_invoice": True,
                }
            )
            if invoice_new_partner.amount_total_signed < 0.0:
                for il in invoice_new_partner.invoice_line_ids:
                    il.quantity *= -1
                invoice_new_partner.move_type = "out_refund"
            invoice_new_partner.sudo().action_post()
            inv_res |= invoice_new_partner
            invoice_refund = Form(
                self.env["account.move"]
                .with_company(final_inv.company_id.id)
                .with_context(
                    default_move_type="out_refund",
                    default_invoice_origin=final_inv.name,
                    default_ref=_("Reversal of: %s, %s")
                    % (final_inv.name, _("Change invoice partner")),
                )
            )
            invoice_refund.partner_id = final_inv.partner_id
            invoice_refund.company_id = final_inv.company_id
            invoice_refund.journal_id = final_inv.journal_id
            invoice_refund.currency_id = final_inv.currency_id
            invoice_refund = invoice_refund.save()
            invoice_line_vals = []
            for il in final_inv.invoice_line_ids.filtered(
                lambda r: not r.down_payment_line_id
            ):
                default_data = {
                    "move_id": invoice_refund.id,
                    "sale_line_ids": [(4, id) for id in il.sale_line_ids.ids],
                }
                invoice_line_vals.append((0, 0, il.copy_data(default=default_data)[0]))

            invoice_refund.write({"invoice_line_ids": invoice_line_vals})
            invoice_refund.sudo().action_post()
            inv_res |= invoice_refund
            final_inv.write({"encounter_final_invoice": False})
            if (
                float_compare(
                    invoice_refund.amount_total,
                    invoice_new_partner.amount_total,
                    precision_rounding=invoice_new_partner.currency_id.rounding,
                )
                != 0
            ):
                raise ValidationError(_("Amount of both invoices must be the same"))
            move_vals = self._change_invoice_partner_move_vals(
                invoice_refund, invoice_new_partner
            )
            move = self.env["account.move"].sudo().create(move_vals)
            move.sudo().action_post()
            ref_iml = invoice_refund.line_ids.filtered(
                lambda r: r.account_id.user_type_id.type in ("receivable", "payable")
            )
            ref_move_iml = move.line_ids.filtered(
                lambda r: (r.partner_id == invoice_refund.partner_id)
            )
            self.env["account.reconciliation.widget"].sudo().process_move_lines(
                [
                    {
                        "mv_line_ids": ref_iml.ids + ref_move_iml.ids,
                        "type": "partner",
                        "id": invoice_refund.partner_id.id,
                        "new_mv_line_dicts": [],
                    }
                ]
            )
            inv_iml = invoice_new_partner.line_ids.filtered(
                lambda r: r.account_id.user_type_id.type in ("receivable", "payable")
            )
            inv_move_iml = move.line_ids.filtered(
                lambda r: r.partner_id == invoice_new_partner.partner_id
            )
            self.env["account.reconciliation.widget"].sudo().process_move_lines(
                [
                    {
                        "mv_line_ids": inv_iml.ids + inv_move_iml.ids,
                        "type": "partner",
                        "id": invoice_new_partner.partner_id.id,
                        "new_mv_line_dicts": [],
                    }
                ]
            )
        for so in final_sos.filtered(lambda r: r.partner_id != partner):
            # TODO : Review what to do on third party invoices
            raise ValidationError(
                _(
                    "Cannot change the Partner of third party invoices for "
                    "%s" % so.name
                )
            )
        if partner not in self.patient_id.related_partner_ids:
            self.patient_id.write({"related_partner_ids": [(4, partner.id)]})
        return inv_res, sos_res

    @api.model
    def _change_invoice_partner_move_vals(self, refund, inv):
        return {
            "journal_id": refund.company_id.change_partner_journal_id.id,
            "ref": _("Reconciliation of credit reinvoiced to another " "customer"),
            "company_id": refund.company_id.id,
            "line_ids": [
                (0, 0, self._change_invoice_partner_iml_vals(refund)),
                (0, 0, self._change_invoice_partner_iml_vals(inv)),
            ],
        }

    @api.model
    def _change_invoice_partner_iml_vals(self, invoice):
        vals = {
            "name": "",
            "account_id": invoice.line_ids.filtered(
                lambda r: r.account_id.user_type_id.type in ("receivable", "payable")
            )
            .mapped("account_id")
            .id,
            "partner_id": invoice.partner_id.id,
            "credit": 0.0,
            "debit": 0.0,
            "currency_id": invoice.currency_id.id
            if invoice.currency_id != invoice.company_id.currency_id
            else False,
        }
        if invoice.move_type in ["out_invoice", "in_refund"]:
            vals["credit"] = invoice.amount_total
        else:
            vals["debit"] = invoice.amount_total
        return vals
