from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    is_medical = fields.Boolean(default=False, readonly=True)
    show_patient = fields.Boolean(default=False, readonly=True)
    show_subscriber = fields.Boolean(default=False, readonly=True)
    show_authorization = fields.Boolean(default=False, readonly=True)
    encounter_id = fields.Many2one('medical.encounter', readonly=True)

    @api.model
    def _prepare_refund(
            self, invoice, date_invoice=None, date=None, description=None,
            journal_id=None):
        vals = super(AccountInvoice, self)._prepare_refund(
            invoice, date_invoice=date_invoice, date=date,
            description=description, journal_id=journal_id)
        vals['is_medical'] = invoice.is_medical
        vals['show_patient'] = invoice.show_patient
        vals['show_subscriber'] = invoice.show_subscriber
        vals['show_authorization'] = invoice.show_authorization
        vals['encounter_id'] = invoice.encounter_id.id
        return vals


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    patient_id = fields.Many2one('medical.patient', readonly=True)
    encounter_id = fields.Many2one('medical.encounter', readonly=True)
    is_medical = fields.Boolean(related='invoice_id.is_medical', readonly=True)
    patient_name = fields.Char()
    subscriber_id = fields.Char()
    authorization_number = fields.Char()
