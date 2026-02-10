# Copyright 2024 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE queue_token_location qtl
        SET origin_request_group_id = mrg.id
        FROM medical_request_group mrg
        WHERE mrg.queue_token_location_id = qtl.id
        """,
    )
