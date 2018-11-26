from odoo import api, models, _
from odoo.exceptions import ValidationError


class MedicalEncounter(models.Model):
    _inherit = 'medical.encounter'

    def _change_invoice_partner(self, partner):
        self.ensure_one()
        partner.ensure_one()
        partner.write({'related_patient_ids': [(4, self.patient_id.id)]})
        so = self.sale_order_ids.filtered(
            lambda r: not r.coverage_agreement_id and not r.is_down_payment
        )
        invoices = so.mapped('invoice_ids')
        sos = self.sale_order_ids.filtered(
            lambda r: r.third_party_order and not r.coverage_agreement_id
        )
        final_inv = invoices.filtered(lambda r: r.encounter_final_invoice)
        final_sos = sos.filtered(lambda r: r.encounter_final_sale_order)
        inv_res = self.env['account.invoice']
        sos_res = self.env['sale.order']
        if not final_inv:
            final_inv = invoices
        if not final_sos:
            final_sos = sos
        if final_inv and final_inv.partner_id != partner:
            invoice_new_partner = self.env['account.invoice'].with_context(
                default_comnpany_id=final_inv.company_id.id,
                force_company=final_inv.company_id.id,
            ).new({
                'partner_id': partner.id,
                'company_id': final_inv.company_id.id,
                'journal_id': final_inv.journal_id.id,
                'type': 'out_invoice',
                'currency_id': final_inv.currency_id.id,
                'encounter_final_invoice': True,
            })
            invoice_new_partner._onchange_partner_id()
            vals = invoice_new_partner._convert_to_write(
                invoice_new_partner._cache)
            invoice_new_partner = self.env['account.invoice'].create(vals)
            for il in final_inv.invoice_line_ids.filtered(
                    lambda r: not r.down_payment_line_id
            ):
                default_data = {
                    'invoice_id': invoice_new_partner.id,
                    'sale_line_ids': [(4, id) for id in il.sale_line_ids.ids]
                }
                if il.invoice_id.type == 'out_refund':
                    default_data['quantity'] = -1 * il.quantity
                il.copy(default=default_data)
            if invoice_new_partner.amount_total_company_signed < 0.0:
                for il in invoice_new_partner.invoice_line_ids:
                    il.quantity *= -1
                invoice_new_partner.type = 'out_refund'
            invoice_new_partner.action_invoice_open()
            inv_res |= invoice_new_partner
            invoice_refund = self.env['account.invoice'].with_context(
                default_comnpany_id=final_inv.company_id.id,
                force_company=final_inv.company_id.id,
            ).new({
                'partner_id': final_inv.partner_id.id,
                'company_id': final_inv.company_id.id,
                'journal_id': final_inv.journal_id.id,
                'type': 'out_refund',
                'currency_id': final_inv.currency_id.id,
            })
            invoice_refund._onchange_partner_id()
            vals = invoice_refund._convert_to_write(
                invoice_refund._cache)
            invoice_refund = self.env['account.invoice'].create(vals)
            for il in final_inv.invoice_line_ids.filtered(
                    lambda r: not r.down_payment_line_id
            ):
                default_data = {
                    'invoice_id': invoice_refund.id,
                    'sale_line_ids': [(4, id) for id in il.sale_line_ids.ids]
                }
                il.copy(default=default_data)
            invoice_refund.action_invoice_open()
            inv_res |= invoice_refund
            final_inv.write({'encounter_final_invoice': False})
            if invoice_refund.amount_total != invoice_new_partner.amount_total:
                raise ValidationError(_(
                    'Amount of both invoices must be the same'
                ))
            move_vals = self._change_invoice_partner_move_vals(
                invoice_refund, invoice_new_partner
            )
            move = self.env['account.move'].create(move_vals)
            move.post()
            ref_iml = invoice_refund.mapped('move_id.line_ids').filtered(
                lambda r: (
                    r.account_id == invoice_refund.account_id and
                    r.partner_id == invoice_refund.partner_id))
            ref_move_iml = move.line_ids.filtered(
                lambda r: (
                    r.account_id == invoice_refund.account_id and
                    r.partner_id == invoice_refund.partner_id))
            self.env['account.move.line'].process_reconciliations(
                [{'mv_line_ids': ref_iml.ids + ref_move_iml.ids,
                  'type': 'partner',
                  'id': invoice_refund.partner_id.id,
                  'new_mv_line_dicts': []}])
            inv_iml = invoice_new_partner.mapped('move_id.line_ids').filtered(
                lambda r: (
                    r.account_id == invoice_new_partner.account_id and
                    r.partner_id == invoice_new_partner.partner_id))
            inv_move_iml = move.line_ids.filtered(
                lambda r: (
                    r.account_id == invoice_new_partner.account_id and
                    r.partner_id == invoice_new_partner.partner_id))
            self.env['account.move.line'].process_reconciliations(
                [{'mv_line_ids': inv_iml.ids + inv_move_iml.ids,
                  'type': 'partner',
                  'id': invoice_new_partner.partner_id.id,
                  'new_mv_line_dicts': []}])
        for so in final_sos.filtered(lambda r: r.partner_id != partner):
            # TODO : Review what to do on third party invoices
            raise ValidationError(_(
                'Cannot change the Partner of third party invoices for '
                '%s' % so.name
            ))
        if partner not in self.patient_id.related_partner_ids:
            self.patient_id.write({
                'related_partner_ids':  [(4, partner.id)],
            })
        return inv_res, sos_res

    @api.model
    def _change_invoice_partner_move_vals(self, refund, inv):
        return {
            'journal_id': refund.company_id.change_partner_journal_id.id,
            'ref': _('Reconciliation of credit reinvoiced to another '
                     'customer'),
            'company_id': refund.company_id.id,
            'line_ids': [(0, 0, self._change_invoice_partner_iml_vals(refund)),
                         (0, 0, self._change_invoice_partner_iml_vals(inv))]
        }

    @api.model
    def _change_invoice_partner_iml_vals(self, invoice):
        vals = {
            'name': '',
            'account_id': invoice.account_id.id,
            'partner_id': invoice.partner_id.id,
            'credit': 0.0,
            'debit': 0.0,
            'currency_id': invoice.currency_id.id,
        }
        if invoice.type in ['out_invoice', 'in_refund']:
            vals['credit'] = invoice.amount_total
        else:
            vals['debit'] = invoice.amount_total
        return vals
