# Copyright 2021 Creu Blanca - Alba Riera

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move_line aml
        SET down_payment_line_id = aml2.id
        FROM account_invoice_line ail
        INNER JOIN account_move_line aml2
            ON aml2.old_invoice_line_id = ail.down_payment_line_id
        WHERE ail.id = aml.old_invoice_line_id
            and ail.down_payment_line_id is not null""",
    )
