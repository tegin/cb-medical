from odoo import fields, models


class SearchEncountersWizard(models.TransientModel):
    _name = "search_encounters.wizard"
    _description = "Search Encounters Wizard"

    code = fields.Char(string="Internal Identifier")

    def search_encounter(self):

        encounter = self.env["medical.encounter"].search(
            [("internal_identifier", "=", self.code)], limit=1
        )
        encounter_commissions = (
            encounter.sale_order_ids.order_line.invoice_lines.agent_ids
        )

        return {
            "id": encounter.id,
            "internal_identifier": encounter.internal_identifier,
            "commissions": [
                {
                    "name": commission.object_id.name,
                    "amount": commission.amount,
                    "invoice": commission.invoice_id.name,
                }
                for commission in encounter_commissions.filtered(
                    lambda r: r.agent_id.id == self.env.user.partner_id.id
                )
            ],
        }
