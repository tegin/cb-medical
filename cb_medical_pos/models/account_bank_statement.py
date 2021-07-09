# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    def _get_opening_balance(self, journal_id):
        if self.env.context.get("ignore_balance_start", False):
            return 0
        return super()._get_opening_balance(journal_id)
