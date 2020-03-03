# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class MedicalLaboratoryRequest(models.Model):
    _inherit = "medical.laboratory.request"

    laboratory_service_ids = fields.Many2many(
        "medical.laboratory.service", readonly=True
    )
    laboratory_event_ids = fields.One2many(
        string="Laboratory Events",
        states={
            "draft": [("readonly", False)],
            "active": [("readonly", False)],
        }
    )
