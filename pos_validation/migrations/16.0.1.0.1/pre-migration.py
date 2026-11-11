# Copyright 2026 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.add_fields(
        env,
        [
            (
                "all_automatic",
                "medical.encounter",
                False,
                "boolean",
                False,
                "pos_validation",
            ),
        ],
    )
