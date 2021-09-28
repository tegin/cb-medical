# Copyright 2021 Creu Blanca - Alba Riera

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE pos_payment pp
        SET encounter_id = am.encounter_id
        FROM pos_order po
            INNER JOIN account_move am ON am.id = po.account_move
        WHERE pp.encounter_id IS NULL
            AND pp.pos_order_id = po.id
            AND am.encounter_id IS NOT NULL
    """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE pos_payment pp
        SET encounter_id = so.encounter_id
        FROM pos_order po
            INNER JOIN sale_order so ON so.id = po.account_move
        WHERE pp.encounter_id IS NULL
            AND pp.pos_order_id = po.id
            AND so.encounter_id IS NOT NULL
    """,
    )
