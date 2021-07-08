from odoo import models


class SalePreinvoiceGroup(models.Model):
    _inherit = "sale.preinvoice.group"

    def close(self):
        return super(
            SalePreinvoiceGroup,
            self.with_context(no_change_commission_agent=True),
        ).close()
