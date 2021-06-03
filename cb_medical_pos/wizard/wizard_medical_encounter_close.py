# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class WizardMedicalEncounterClose(models.TransientModel):
    _name = "wizard.medical.encounter.close"
    _description = "wizard.medical.encounter.close"

    pos_session_id = fields.Many2one(
        comodel_name="pos.session",
        string="PoS Session",
        required=True,
        domain=[("state", "=", "opened")],
    )
    encounter_id = fields.Many2one(
        comodel_name="medical.encounter",
        string="encounter",
        readonly=True,
        required=True,
    )

    @api.multi
    def run(self):
        self.ensure_one()
        # It could be changed if it need a finished option
        # self.encounter_id.pos_session_id = self.pos_session_id
        self.encounter_id.with_context(
            pos_session_id=self.pos_session_id.id,
            company_id=self.pos_session_id.config_id.company_id.id,
        ).inprogress2onleave()
