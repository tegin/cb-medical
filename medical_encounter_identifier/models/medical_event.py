from odoo import fields, models


class MedicalEvent(models.AbstractModel):
    _name = "medical.event"
    _inherit = ["medical.event", "medical.cb.identifier"]

    encounter_id = fields.Many2one("medical.encounter", readonly=True)
