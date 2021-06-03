# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class MedicalEvent(models.AbstractModel):
    _name = "medical.event"
    _inherit = ["medical.event", "medical.commission.action"]
