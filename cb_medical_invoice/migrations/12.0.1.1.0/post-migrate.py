# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, SUPERUSER_ID
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(cr, version):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        ResPartner = env["res.partner"]
        for record in ResPartner.search(
            [("self_invoice_sequence_id", "!=", False)]
        ):
            record.self_invoice_refund_sequence_id = (
                env["ir.sequence"]
                .sudo()
                .create(
                    {
                        "name": record.name + " Self invoice refund sequence",
                        "implementation": "no_gap",
                        "number_increment": 1,
                        "padding": 4,
                        "prefix": ResPartner._self_invoice_refund_sequence_prefix(),
                        "use_date_range": True,
                        "number_next": 1,
                    }
                )
            )
