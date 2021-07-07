# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models, _
from odoo.exceptions import ValidationError

SO_OPEN = ["draft"]


class MedicalCareplan(models.Model):
    _inherit = "medical.careplan"

    @api.onchange("encounter_id")
    def _onchange_encounter(self):
        for record in self:
            record.center_id = self.encounter_id.center_id

    def get_payor(self):
        if self.sub_payor_id:
            return self.sub_payor_id.id
        return self.payor_id.id

    def _add_request_group(
        self,
        service=False,
        qty=1,
        order_by=False,
        authorization_number=False,
        performer=False,
        **kwargs
    ):
        self.ensure_one()
        if not service:
            raise ValidationError(_("Service is required"))
        if isinstance(service, int):
            service = self.env["product.product"].browse(service)
        if not order_by:
            order_by = self.env["res.partner"]
        elif isinstance(order_by, int):
            order_by = self.env["res.partner"].browse(order_by)
        if not performer:
            performer = self.env["res.partner"]
        elif isinstance(performer, int):
            performer = self.env["res.partner"].browse(performer)
        call = (
            self.env["medical.careplan.add.plan.definition"]
            .with_context(default_careplan_id=self.id)
            .create(
                {
                    "order_by_id": order_by.id or False,
                    "authorization_number": authorization_number,
                    "qty": qty,
                }
            )
        )
        agreement_line = self.env["medical.coverage.agreement.item"].search(
            [
                ("product_id", "=", service.id),
                ("coverage_agreement_id", "in", call.agreement_ids.ids),
                ("plan_definition_id", "!=", False),
            ],
            limit=1,
        )
        agreement_line.ensure_one()
        write_vals = {"agreement_line_id": agreement_line.id}
        if agreement_line.plan_definition_id.performer_required:
            if isinstance(performer, int):
                performer = self.env["res.partner"].browse(performer)
            write_vals["performer_id"] = performer.id
        call.write(write_vals)
        return call._run()
