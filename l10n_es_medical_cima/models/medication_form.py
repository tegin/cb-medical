# Copyright 2022 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicationForm(models.Model):

    _inherit = "medication.form"

    cima_ref = fields.Char()


class MedicalAdministrationRoute(models.Model):

    _inherit = "medical.administration.route"

    cima_ref = fields.Char()
