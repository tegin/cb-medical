# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move_line aml
        SET guard_id = ail.guard_id
        FROM account_invoice_line ail
        WHERE ail.id = aml.old_invoice_line_id AND ail.guard_id is not NULL""",
    )
