# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalQuote(models.Model):

    _inherit = "medical.quote"

    lead_id = fields.Many2one("crm.lead")
