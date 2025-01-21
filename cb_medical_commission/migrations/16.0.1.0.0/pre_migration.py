# Copyright 2025 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

_field_renames = [
    ("sale.order.line.agent", "sale_order_line_agent", "date", "invoice_date"),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, _field_renames)
