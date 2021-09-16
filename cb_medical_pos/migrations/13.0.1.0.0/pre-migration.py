# Copyright 2021 Creu Blanca - Alba Riera

from openupgradelib import openupgrade

_column_renames = {
    "sale_order_line": [("down_payment_line_id", None)],
}


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_columns(env.cr, _column_renames)
