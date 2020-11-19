# Copyright 2020 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, _version):
    openupgrade.logged_query(
        env.cr,
        """
            UPDATE mgmtsystem_nonconformity nc
            SET res_id = nc.encounter_id, res_model = 'medical.encounter'
            WHERE nc.encounter_id IS NOT NULL
            """,
    )
    openupgrade.logged_query(
        env.cr,
        """
            UPDATE mgmtsystem_quality_issue qi
            SET res_id = qi.encounter_id, res_model = 'medical.encounter'
            WHERE qi.encounter_id IS NOT NULL
            """,
    )
