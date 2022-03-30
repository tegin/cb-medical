# Copyright 2022 Creu Blanca
import datetime

import freezegun
from odoo.tests.common import TransactionCase


class TestMedicalProductRequestOrder(TransactionCase):
    def setUp(self):
        super(TestMedicalProductRequestOrder, self).setUp()
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

    def test_dispensation_date_request_with_today_date(self):
        request = self.external_product_request_order
        request.expected_dispensation_date = False
        with freezegun.freeze_time("2022-01-01"):
            request.complete_action()
        self.assertEqual(
            request.expected_dispensation_date, datetime.date(2022, 1, 1)
        )

    def test_dispensation_date_request_with_date(self):
        request = self.env["medical.product.request.order"].create(
            {
                "category": "discharge",
                "patient_id": self.patient.id,
                "expected_dispensation_date": datetime.datetime(2022, 2, 1),
            }
        )
        request.complete_action()
        self.assertEqual(
            request.expected_dispensation_date, datetime.date(2022, 2, 1)
        )

    def test_order_request_center_id(self):
        center_2 = self.env["res.partner"].create(
            {
                "name": "center",
                "is_center": True,
                "is_medical": True,
                "encounter_sequence_prefix": "C2",
            }
        )
        self.env["ir.config_parameter"].set_param(
            "cb.prescription_default_center_id", center_2.id
        )
        self.assertEqual(
            self.external_product_request_order.center_id.id,
            self.encounter.center_id.id,
        )
        self.external_product_request_order.encounter_id = False
        self.assertEqual(
            self.external_product_request_order.center_id.id, center_2.id
        )
