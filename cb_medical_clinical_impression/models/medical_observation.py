# Copyright 2024 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalObservation(models.Model):

    _inherit = "medical.observation"

    impression_id = fields.Many2one("medical.clinical.impression")

    def _get_impression_data(self):
        return {
            "id": self.id,
            "concept_id": self.concept_id.id,
            "selection_options": self.selection_options,
            "name": self.name,
            "value_bool": self.value_bool,
            "value_str": self.value_str,
            "value_float": self.value_float,
            "value_date": fields.Date.to_string(self.value_date),
            "value_int": self.value_int,
            "value_selection": self.value_selection,
            "uom_id": self.uom_id.id,
            "uom": self.uom,
            "value_type": self.value_type,
        }
