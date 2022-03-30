# Copyright 2022 Creu Blanca
import datetime

import freezegun
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestMedicalProductRequest(TransactionCase):
    def setUp(self):
        super(TestMedicalProductRequest, self).setUp()
        self.center = self.env["res.partner"].create(
            {
                "name": "center",
                "is_center": True,
                "is_medical": True,
                "encounter_sequence_prefix": "C",
            }
        )
        self.patient = self.env["medical.patient"].create({"name": "Patient"})
        self.encounter = self.env["medical.encounter"].create(
            {"patient_id": self.patient.id, "center_id": self.center.id}
        )
        self.tablet_uom = self.env["uom.uom"].create(
            {
                "name": "Tablets",
                "category_id": self.env.ref("uom.product_uom_categ_unit").id,
                "factor": 1.0,
                "uom_type": "bigger",
                "rounding": 0.001,
            }
        )
        self.tablet_form = self.env["medication.form"].create(
            {
                "name": "EFG film coated tablets",
                "uom_ids": [(4, self.tablet_uom.id)],
            }
        )
        self.test_product_template = self.env[
            "medical.product.template"
        ].create(
            {
                "name": "Test name",
                "product_type": "medication",
                "ingredients": "Test name",
                "dosage": "600 mg",
                "form_id": self.tablet_form.id,
            }
        )
        self.test_product_30_tablets = self.env[
            "medical.product.product"
        ].create(
            {
                "product_tmpl_id": self.test_product_template.id,
                "amount": 30,
                "amount_uom_id": self.tablet_uom.id,
            }
        )
        self.test_template_lab = self.env[
            "medical.product.template.commercial"
        ].create(
            {
                "product_tmpl_id": self.test_product_template.id,
                "laboratory": "Lab test",
                "code": "70039",
                "laboratory_product_name": "labname",
            }
        )
        self.test_template_30_tablets_lab = self.env[
            "medical.product.product.commercial"
        ].create(
            {
                "medical_product_id": self.test_product_30_tablets.id,
                "product_tmpl_commercial_id": self.test_template_lab.id,
                "code": "661765",
            }
        )
        self.external_product_request_order = self.env[
            "medical.product.request.order"
        ].create(
            {
                "category": "discharge",
                "patient_id": self.patient.id,
            }
        )
        self.external_product_request = self.env[
            "medical.product.request"
        ].create(
            {
                "request_order_id": self.external_product_request_order.id,
                "medical_product_template_id": self.test_product_template.id,
                "dose_quantity": 1,
                "dose_uom_id": self.tablet_uom.id,
                "rate_quantity": 3,
                "rate_uom_id": self.env.ref("uom.product_uom_day").id,
                "duration": 60,
                "duration_uom_id": self.env.ref("uom.product_uom_day").id,
            }
        )
        self.internal_product_request_order = self.env[
            "medical.product.request.order"
        ].create(
            {
                "category": "inpatient",
                "patient_id": self.patient.id,
            }
        )
        self.internal_product_request = self.env[
            "medical.product.request"
        ].create(
            {
                "request_order_id": self.internal_product_request_order.id,
                "medical_product_template_id": self.test_product_template.id,
                "dose_quantity": 1,
                "dose_uom_id": self.tablet_uom.id,
                "rate_quantity": 3,
                "rate_uom_id": self.env.ref("uom.product_uom_day").id,
                "duration": 5,
                "duration_uom_id": self.env.ref("uom.product_uom_day").id,
            }
        )

    def test_expected_dispensation_date_if_has_order_id(self):
        self.assertFalse(
            self.external_product_request.expected_dispensation_date
        )
        self.assertTrue(self.external_product_request_order)
        self.external_product_request_order.complete_action()
        self.assertEqual(
            self.external_product_request_order.expected_dispensation_date,
            self.external_product_request.expected_dispensation_date,
        )

    def test_expected_dispensation_date_if_has_not_order_id(self):
        # With expected dispensation date
        request = self.env["medical.product.request"].create(
            {
                "medical_product_template_id": self.test_product_template.id,
                "dose_quantity": 1,
                "dose_uom_id": self.tablet_uom.id,
                "rate_quantity": 3,
                "rate_uom_id": self.env.ref("uom.product_uom_day").id,
                "duration": 60,
                "duration_uom_id": self.env.ref("uom.product_uom_day").id,
                "expected_dispensation_date": datetime.date(2022, 1, 1),
            }
        )
        request.complete_action()
        self.assertTrue(request.expected_dispensation_date)
        self.assertEqual(
            request.expected_dispensation_date, datetime.date(2022, 1, 1)
        )
        # Without expected dispensation date
        request_2 = self.env["medical.product.request"].create(
            {
                "medical_product_template_id": self.test_product_template.id,
                "dose_quantity": 1,
                "dose_uom_id": self.tablet_uom.id,
                "rate_quantity": 3,
                "rate_uom_id": self.env.ref("uom.product_uom_day").id,
                "duration": 60,
                "duration_uom_id": self.env.ref("uom.product_uom_day").id,
            }
        )
        with freezegun.freeze_time("2022-02-02"):
            request_2.complete_action()
        self.assertEqual(
            request_2.expected_dispensation_date, datetime.date(2022, 2, 2)
        )

    def test_specific_rate_constrain(self):
        with self.assertRaises(ValidationError):
            self.internal_product_request.specific_rate = 0

    def test_compute_rate_from_specific_rate(self):
        # Specific Rate: Every 8 hours -> Rate: 3 times /day
        request = self.env["medical.product.request"].create(
            {
                "medical_product_template_id": self.test_product_template.id,
                "dose_quantity": 1,
                "dose_uom_id": self.tablet_uom.id,
                "specific_rate": 8,
                "specific_rate_uom_id": self.env.ref(
                    "uom.product_uom_hour"
                ).id,
                "duration": 30,
                "duration_uom_id": self.env.ref("uom.product_uom_day").id,
            }
        )
        self.assertEqual(request.rate_quantity, 3)
        self.assertEqual(
            request.rate_uom_id.id, self.env.ref("uom.product_uom_day").id
        )

        # Specific Rate: Every 48 hours -> Rate: 3.5 times/week
        request.specific_rate = 48
        request.specific_rate_uom_id = self.env.ref("uom.product_uom_hour").id
        self.assertEqual(request.rate_quantity, 3.5)
        self.assertEqual(
            request.rate_uom_id.id,
            self.env.ref("cb_medical_product_request.product_uom_week").id,
        )

        # Specific Rate: Every 2 days -> Rate: 3.5 times/week
        request.specific_rate = 2
        request.specific_rate_uom_id = self.env.ref("uom.product_uom_day").id
        self.assertEqual(request.rate_quantity, 3.5)
        self.assertEqual(
            request.rate_uom_id.id,
            self.env.ref("cb_medical_product_request.product_uom_week").id,
        )

        # Specific Rate: Every 1 week -> Rate: 1 times /week
        request.specific_rate = 1
        request.specific_rate_uom_id = self.env.ref(
            "cb_medical_product_request.product_uom_week"
        ).id
        self.assertEqual(request.rate_quantity, 1)
        self.assertEqual(
            request.rate_uom_id.id,
            self.env.ref("cb_medical_product_request.product_uom_week").id,
        )
