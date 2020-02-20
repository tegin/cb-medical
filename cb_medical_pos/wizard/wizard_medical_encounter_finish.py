# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class WizardMedicalEncounterClose(models.TransientModel):
    _name = "wizard.medical.encounter.finish"
    _description = 'wizard.medical.encounter.finish'

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
    pos_config_id = fields.Many2one(
        "pos.config", related="pos_session_id.config_id", readonly=True
    )
    journal_ids = fields.Many2many(
        "account.journal",
        related="pos_session_id.config_id.journal_ids",
        readonly=True,
    )
    journal_id = fields.Many2one(
        "account.journal", domain="[('id', 'in', journal_ids)]", required=True
    )
    currency_id = fields.Many2one(
        "res.currency", related="journal_id.currency_id", readonly=True
    )
    amount = fields.Monetary(
        related="encounter_id.pending_private_amount", readonly=True
    )

    @api.onchange("pos_session_id")
    def _onchange_session(self):
        self.journal_id = False

    @api.multi
    def run(self):
        self.ensure_one()
        self.encounter_id.with_context(
            pos_session_id=self.pos_session_id.id,
            journal_id=self.journal_id.id,
        ).onleave2finished()
