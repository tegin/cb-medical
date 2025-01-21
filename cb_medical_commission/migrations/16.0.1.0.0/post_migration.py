# Copyright 2025 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    env.ref("cb_medical_commission.commission_01").commission_type = "medical"
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE commission_settlement_line csl
        SET sale_agent_line_id = agent_sale_line_id
        FROM settlement_agent_sale_line_rel rel
        WHERE rel.settlement_id = csl.id
        """,
    )
