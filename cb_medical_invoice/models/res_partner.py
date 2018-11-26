from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    related_patient_ids = fields.Many2many(
        'medical.patient',
        'medical_patient_invoicable_partner',
        'partner_id',
        'patient_id',
    )
