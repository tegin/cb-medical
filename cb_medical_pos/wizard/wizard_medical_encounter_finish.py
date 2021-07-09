# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class WizardMedicalEncounterFinish(models.TransientModel):
    _name = "wizard.medical.encounter.finish"
    _description = "wizard.medical.encounter.finish"

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
    payment_method_ids = fields.Many2many(
        "pos.payment.method",
        related="pos_session_id.config_id.payment_method_ids",
        readonly=True,
    )
    payment_method_id = fields.Many2one(
        "pos.payment.method",
        domain="[('id', 'in', payment_method_ids)]",
        required=True,
    )
    currency_id = fields.Many2one(
        "res.currency", related="pos_session_id.currency_id", readonly=True
    )
    amount = fields.Monetary(
        related="encounter_id.pending_private_amount", readonly=True
    )
    dont_pay = fields.Boolean()

    @api.onchange("pos_session_id")
    def _onchange_session(self):
        self.payment_method_id = False

    def run(self):
        self.ensure_one()
        self.encounter_id.with_context(
            pos_session_id=self.pos_session_id.id,
            payment_method_id=self.payment_method_id.id,
            encounter_finish_dont_pay=self.dont_pay,
        ).onleave2finished()
