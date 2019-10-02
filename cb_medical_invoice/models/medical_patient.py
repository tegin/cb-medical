from odoo import fields, models


class MedicalPatient(models.Model):
    _inherit = "medical.patient"

    related_partner_ids = fields.Many2many(
        "res.partner",
        "medical_patient_invoicable_partner",
        "patient_id",
        "partner_id",
    )
