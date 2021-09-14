# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
    UPDATE res_partner rp
    SET delegated_agent_id = car.agent_id
    FROM commission_agent_rel car
    WHERE car.partner_id = rp.id
    """,
    )
