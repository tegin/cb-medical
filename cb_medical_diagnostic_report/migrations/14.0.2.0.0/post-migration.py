# Copyright 2022 Creu Blanca
# License AGPL-3.0 or later (https://www.gnuorg/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env.cr,
        "cb_medical_diagnostic_report",
        "migrations/14.0.2.0.0/noupdate_changes.xml",
    )
