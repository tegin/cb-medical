# Copyright 2021 Creu Blanca - Alba Riera

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move am
        SET bank_statement_line_ids = ai.bank_statement_line_ids,
        FROM account_invoice ai
        WHERE ai.id = am.old_invoice_id and ai.bank_statement_line_ids is not null""",
    )

    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move_line aml
        SET down_payment_line_id = ail.down_payment_line_id,
        FROM account_invoice_line ail
        WHERE ail.id = aml.old_invoice_id and ail.down_payment_line_id is not null""",
    )
