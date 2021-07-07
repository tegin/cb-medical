# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE sale_preinvoice_group spg
        SET move_id = am.id
        FROM account_move am
        WHERE am.old_invoice_id = spg.invoice_id
        """,
    )

    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move am
        SET agreement_id = ai.agreement_id,
            coverage_template_id = ai.coverage_template_id,
            invoice_group_method_id = ai.invoice_group_method_id
        FROM account_invoice ai
        WHERE ai.id = am.old_invoice_id""",
    )
