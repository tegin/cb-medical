# Copyright 2023 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MedicalRequestGroup(models.Model):

    _inherit = "medical.request.group"

    queue_token_location_id = fields.Many2one("queue.token.location", readonly=True)

    @api.constrains(
        "performer_id", "center_id", "encounter_id", "plan_definition_id", "fhir_state"
    )
    def _check_queue_token(self):
        for record in self:
            record._review_queue_token()

    def _clean_queue_token(self):
        if self.queue_token_location_id:
            # TODO: Maybe we should cancell in-progress or finished jobs, isn't it :S
            if self.queue_token_location_id.state == "draft":
                self.queue_token_location_id.state = "cancelled"
            self.queue_token_location_id = False
        return False

    def _review_queue_token(self):
        if self.fhir_state == "cancelled":
            return self._clean_queue_token()
        if not self.plan_definition_id.generate_queue_task:
            return self._clean_queue_token()
        return getattr(
            self, "_review_queue_token_%s" % self.plan_definition_id.generate_queue_task
        )()

    def _review_queue_token_performer(self):
        location_area = self.performer_id.queue_location_ids.filtered(
            lambda r: r.center_id == self.center_id
        )
        if not location_area:
            location_area = self.performer_id.queue_location_ids.filtered(
                lambda r: not r.center_id
            )
        if not location_area:
            return self._clean_queue_token()
        return self._manage_queue_token(
            location=location_area.location_id, group=location_area.group_id
        )

    def _review_queue_token_area(self):
        area = self.plan_definition_id.queue_area_id
        location_area = area.location_ids.filtered(
            lambda r: r.center_id == self.center_id
        )
        if not location_area:
            return self._clean_queue_token()
        return self._manage_queue_token(
            location=location_area.location_id, group=location_area.group_id
        )

    def _manage_queue_token(self, location=False, group=False):
        if not location and not group:
            return self._clean_queue_token()
        if location and group:
            raise ValidationError(
                _("Location and Group cannot be defined at the same time")
            )
        if self.queue_token_location_id:
            if self.queue_token_location_id.state in ["draft"]:
                self.queue_token_location_id.write(
                    {
                        "location_id": location and location.id,
                        "group_id": group and group.id,
                    }
                )
            return self.queue_token_location_id
        return self._create_queue_token(location=location, group=group)

    def _create_queue_token(self, location=False, group=False):
        self.queue_token_location_id = self.env["queue.token.location"].create(
            self._create_queue_token_vals(location=location, group=group)
        )
        return self.queue_token_location_id

    def _create_queue_token_vals(self, location=False, group=False):
        token = self.encounter_id._get_queue_token()
        return {
            "group_id": group and group.id,
            "location_id": location and location.id,
            "token_id": token.id,
        }
