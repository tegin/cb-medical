from odoo import models, fields


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    is_medical = fields.Boolean(default=False, readonly=True)
    show_patient = fields.Boolean(default=False, readonly=True)
    show_subscriber = fields.Boolean(default=False, readonly=True)
    show_authorization = fields.Boolean(default=False, readonly=True)


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    patient_id = fields.Many2one('medical.patient', readonly=True)
    encounter_id = fields.Many2one('medical.encounter', readonly=True)
    is_medical = fields.Boolean(related='invoice_id.is_medical', readonly=True)
    patient_name = fields.Char()
    subscriber_id = fields.Char()
    authorization_number = fields.Char()
