# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, time, timedelta

from dateutil import tz
from odoo import fields, models
from pytz import utc


class MedicalTurnSpecialty(models.Model):
    _name = "medical.turn.specialty"
    _description = "Turn Specialty"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    rule_ids = fields.One2many(
        "medical.turn.specialty.rule",
        inverse_name="turn_specialty_id",
        copy=True,
    )

    practitioner_ids = fields.Many2many(
        "res.partner",
        string="Practitioners",
        domain=[("is_practitioner", "=", True)],
    )
    turn_tag_ids = fields.Many2many(comodel_name="medical.turn.tag")

    def _execute_rules(self, start_date, end_date):
        results = self.env["medical.turn"]
        rules = self.mapped("rule_ids")
        for day in range(0, (end_date - start_date).days):
            date = start_date + timedelta(days=day)
            for rule in rules:
                if date.weekday() != int(rule.dayofweek):
                    continue
                results |= rule._generate_record(date)
        return results


class MedicalTurnSpecialtyRule(models.Model):
    _name = "medical.turn.specialty.rule"
    _description = "medical.turn.specialty.rule"

    turn_specialty_id = fields.Many2one(
        "medical.turn.specialty", required=True, ondelete="cascade"
    )
    default_practitioner_id = fields.Many2one("res.partner")
    dayofweek = fields.Selection(
        [
            ("0", "Monday"),
            ("1", "Tuesday"),
            ("2", "Wednesday"),
            ("3", "Thursday"),
            ("4", "Friday"),
            ("5", "Saturday"),
            ("6", "Sunday"),
        ],
        "Day of Week",
        required=True,
        index=True,
        default="0",
    )
    start_hour = fields.Float(required=True)
    duration = fields.Float(required=True)
    center_ids = fields.Many2many(
        string="Centers",
        required=True,
        comodel_name="res.partner",
        domain=[("is_center", "=", True)],
        tracking=True,
    )

    def _generate_record(self, date):
        utz = self.env.user.tz
        rule_date = (
            datetime.combine(date, time(0, 0, 0, 0, tzinfo=None))
            + timedelta(hours=self.start_hour)
        ).replace(tzinfo=tz.gettz(utz))
        return self.env["medical.turn"].create(
            self._generate_record_vals(rule_date)
        )

    def _generate_record_vals(self, rule_date):
        return {
            "specialty_id": self.turn_specialty_id.id,
            "duration": self.duration,
            "practitioner_id": self.default_practitioner_id.id or False,
            "center_ids": [(6, 0, self.center_ids.ids)],
            "date": fields.Datetime.to_string(rule_date.astimezone(utc)),
        }
