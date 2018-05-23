from odoo import api, fields, models
from odoo.addons.base.ir.ir_sequence import _update_nogap


class MedicalEncounter(models.Model):
    _inherit = 'medical.encounter'

    number_next = fields.Integer(default=1)
    # We must keep this name in order to use _update_nogap function

    @api.multi
    def get_next_number(self):
        self.ensure_one()
        return _update_nogap(self, 1)

    @api.multi
    def get_next_number_cb(self, format):
        self.ensure_one()
        return format % self.get_next_number()
