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
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE sale_order_line sol
        SET down_payment_line_id = aml.id
        FROM account_move_line aml
        WHERE aml.old_invoice_line_id = sol.{}
            AND sol.down_payment_line_id is NOT NULL""".format(
            openupgrade.get_legacy_name("down_payment_line_id")
        ),
    )
    openupgrade.logged_query(
        env.cr,
        """
            SELECT
                absl.id,
                ps.id as session_id,
                COALESCE(absl.invoice_id, so.third_party_move_id) as account_move,
                absl.sale_order_id,
                absl.amount,
                absl.partner_id,
                COALESCE(aj.currency_id, rc.currency_id) as currency_id
            FROM
                pos_session ps
                JOIN pos_config pc ON pc.id = ps.config_id
                JOIN account_bank_statement_line absl ON absl.pos_session_id = ps.id
                JOIN account_bank_statement abs ON abs.id = absl.statement_id
                JOIN account_journal aj ON aj.id = abs.journal_id
                JOIN res_company rc ON rc.id = aj.company_id
                LEFT JOIN sale_order so ON so.id = absl.sale_order_id
            WHERE ps.state != 'closed'
                AND (
                    absl.invoice_id is NOT NULL
                    OR absl.sale_order_id IS NOT NULL
                )
        """,
    )
    data = env.cr.fetchall()
    for d in data:
        order = env["pos.order"].create(
            {
                "amount_total": d[4],
                "currency_id": d[6],
                "partner_id": d[5],
                "sale_order_id": d[3],
                "session_id": d[1],
                "amount_tax": 0,
                "amount_paid": d[4],
                "amount_return": 0,
                "account_move": d[2],
            }
        )
        order.state = "invoiced"
        env.cr.execute(
            """
                UPDATE account_bank_statement_line
                SET pos_statement_id = %s
                WHERE id = %s
            """,
            (order.id, d[0]),
        )
