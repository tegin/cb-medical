# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
            DELETE FROM ir_model_relation imr
            USING ir_model im
            WHERE imr.model = im.id
                AND im.model = 'wizard.sale.preinvoice.group.barcode'""",
    )
