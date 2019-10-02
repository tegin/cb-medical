from datetime import timedelta
from odoo.exceptions import UserError, ValidationError
from odoo.fields import Date, Datetime
from odoo.tests.common import TransactionCase


class TestMedicalGuard(TransactionCase):
    def setUp(self):
        super().setUp()
        self.journal = self.env["account.journal"].search(
            [("type", "=", "purchase")], limit=1
        )
        self.product = self.env["product.product"].create(
            {
                "type": "service",
                "name": "Product",
                "standard_price": 100,
                "supplier_taxes_id": [],
            }
        )
        self.center = self.env["res.partner"].create(
            {
                "name": "Center",
                "is_center": True,
                "is_medical": True,
                "guard_journal_id": self.journal.id,
            }
        )
        self.practitioner = self.env["res.partner"].create(
            {
                "name": "Practitioner",
                "is_practitioner": True,
                "is_medical": True,
            }
        )

    def test_complex_plan(self):
        plan = self.env["medical.guard.plan"].create(
            {
                "location_id": self.center.id,
                "product_id": self.product.id,
                "start_time": 0,
                "delay": 1,
                "weekday": "*",
                "monthday": "*",
                "month": "*",
            }
        )
        self.assertFalse(
            self.env["medical.guard"].search([("plan_guard_id", "=", plan.id)])
        )
        plan.monthday = "1-40"
        date = Date.from_string(Date.today()).replace(day=1)
        with self.assertRaises(UserError):
            self.env["medical.guard.plan.apply"].create(
                {
                    "start_date": Date.to_string(date),
                    "end_date": Date.to_string(date + timedelta(days=1)),
                }
            ).run()
        plan.monthday = "1%"
        with self.assertRaises(UserError):
            self.env["medical.guard.plan.apply"].create(
                {
                    "start_date": Date.to_string(date),
                    "end_date": Date.to_string(date + timedelta(days=1)),
                }
            ).run()
        plan.monthday = "AB/2"
        with self.assertRaises(UserError):
            self.env["medical.guard.plan.apply"].create(
                {
                    "start_date": Date.to_string(date),
                    "end_date": Date.to_string(date + timedelta(days=1)),
                }
            ).run()
        plan.monthday = "*/2"
        self.env["medical.guard.plan.apply"].create(
            {
                "start_date": Date.to_string(date + timedelta(days=1)),
                "end_date": Date.to_string(date + timedelta(days=1)),
            }
        ).run()
        self.assertFalse(
            self.env["medical.guard"].search([("plan_guard_id", "=", plan.id)])
        )
        plan.monthday = "15-20"
        self.env["medical.guard.plan.apply"].create(
            {
                "start_date": Date.to_string(date),
                "end_date": Date.to_string(date + timedelta(days=1)),
            }
        ).run()
        self.assertFalse(
            self.env["medical.guard"].search([("plan_guard_id", "=", plan.id)])
        )
        plan.monthday = "15-5"
        self.env["medical.guard.plan.apply"].create(
            {
                "start_date": Date.to_string(date),
                "end_date": Date.to_string(date + timedelta(days=1)),
            }
        ).run()
        self.assertTrue(
            self.env["medical.guard"].search([("plan_guard_id", "=", plan.id)])
        )

    def check_apply_plan(self, key, value, modulus, difference):
        plan = self.env["medical.guard.plan"].create(
            {
                "location_id": self.center.id,
                "product_id": self.product.id,
                "start_time": 0,
                "delay": 1,
                "weekday": "*",
                "monthday": "*",
                "month": "*",
            }
        )
        self.assertFalse(
            self.env["medical.guard"].search([("plan_guard_id", "=", plan.id)])
        )
        plan.write({key: ((value + 1) % modulus) + difference})
        self.env["medical.guard.plan.apply"].create(
            {
                "start_date": Date.today(),
                "end_date": Date.to_string(Date.from_string(Date.today())),
            }
        ).run()
        self.assertFalse(
            self.env["medical.guard"].search([("plan_guard_id", "=", plan.id)])
        )
        plan.write({key: value})
        self.env["medical.guard.plan.apply"].create(
            {
                "start_date": Date.today(),
                "end_date": Date.to_string(Date.from_string(Date.today())),
            }
        ).run()
        self.assertTrue(
            self.env["medical.guard"].search([("plan_guard_id", "=", plan.id)])
        )

    def test_apply_weekday_plan(self):
        self.check_apply_plan(
            "weekday", Date.from_string(Date.today()).weekday(), 7, 0
        )

    def test_apply_month_plan(self):
        self.check_apply_plan(
            "month", Date.from_string(Date.today()).month, 12, 1
        )

    def test_apply_monthday_plan(self):
        self.check_apply_plan(
            "monthday", Date.from_string(Date.today()).day, 25, 1
        )

    def test_completion(self):
        guard = self.env["medical.guard"].create(
            {
                "product_id": self.product.id,
                "location_id": self.center.id,
                "date": Datetime.now(),
                "delay": 1,
            }
        )
        self.assertEqual(guard.state, "draft")
        with self.assertRaises(ValidationError):
            guard.complete()
        guard.practitioner_id = self.practitioner
        guard.complete()
        self.assertEqual(guard.state, "completed")
        self.assertFalse(guard.invoice_line_ids)
        self.env["medical.guard.invoice"].create(
            {"date_from": Date.today(), "date_to": Date.today()}
        ).run()
        guard.refresh()
        self.assertTrue(guard.invoice_line_ids)
        self.assertEqual(guard.invoice_line_ids.invoice_id.amount_total, 100)
