# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class WizardMedicalCareplanClose(models.TransientModel):
    _name = 'wizard.medical.careplan.close'

    pos_session_id = fields.Many2one(
        comodel_name='pos.session',
        string='PoS Session',
        required=True,
        domain=[('state', '=', 'opened')]
    )
    careplan_id = fields.Many2one(
        comodel_name='medical.careplan',
        string='Careplan',
        readonly=True,
        required=True
    )

    @api.multi
    def run(self):
        self.ensure_one()
        self.careplan_id.pos_session_id = self.pos_session_id
        self.careplan_id.active2completed()
