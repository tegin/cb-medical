# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    env["medical.guard"].search([]).product_id.product_tmpl_id.write(
        {
            "is_guard": True,
            "is_invoiceable_guard": True,
        }
    )
