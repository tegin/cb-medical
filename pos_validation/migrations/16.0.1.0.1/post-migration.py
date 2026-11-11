# Copyright 2026 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    env["medical.encounter"].search(
        [("validation_status", "!=", "finished")]
    )._compute_validation_values()
