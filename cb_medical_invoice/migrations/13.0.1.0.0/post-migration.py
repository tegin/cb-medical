# Copyright 2021 Creu Blanca - Alba Riera

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move am
        SET encounter_final_invoice = ai.encounter_final_invoice,
        FROM account_invoice ai
        WHERE ai.id = am.old_invoice_id""",
    )
