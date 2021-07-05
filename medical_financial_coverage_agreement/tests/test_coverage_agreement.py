# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import logging
from io import BytesIO

import pandas
from odoo.exceptions import ValidationError
from odoo.tests.common import Form, SavepointCase

_logger = logging.getLogger(__name__)


class TestMedicalCoverageAgreement(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestMedicalCoverageAgreement, cls).setUpClass()
        cls.medical_user_group = cls.env.ref(
            "medical_base.group_medical_configurator"
        )
        cls.medical_user = cls._create_user(
            "medical_user", cls.medical_user_group.id
        )
        cls.patient_model = cls.env["medical.patient"]
        cls.coverage_model = cls.env["medical.coverage"]
        cls.coverage_template_model = cls.env["medical.coverage.template"]
        cls.payor_model = cls.env["res.partner"]
        cls.coverage_agreement_model = cls.env["medical.coverage.agreement"]
        cls.coverage_agreement_model_item = cls.env[
            "medical.coverage.agreement.item"
        ]
        cls.center_model = cls.env["res.partner"]
        cls.product_model = cls.env["product.product"]
        cls.type_model = cls.env["workflow.type"]
        cls.act_def_model = cls.env["workflow.activity.definition"]
        cls.action_model = cls.env["workflow.plan.definition.action"]
        cls.plan_model = cls.env["workflow.plan.definition"]
        cls.patient_1 = cls._create_patient()
        cls.patient_2 = cls._create_patient()
        cls.payor_1 = cls._create_payor()
        cls.coverage_template_1 = cls._create_coverage_template()
        cls.coverage = cls._create_coverage(cls.coverage_template_1)
        cls.center_1 = cls._create_center()
        cls.product_1 = cls._create_product("test 1")
        cls.product_2 = cls._create_product("test 2")
        cls.type_1 = cls._create_type()
        cls.act_def_1 = cls._create_act_def()
        cls.plan_1 = cls._create_plan()
        cls.action_1 = cls._create_action()

    @classmethod
    def _create_user(cls, name, group_ids):
        return (
            cls.env["res.users"]
            .with_context({"no_reset_password": True})
            .create(
                {
                    "name": name,
                    "password": "demo",
                    "login": name,
                    "email": "@".join([name, "@test.com"]),
                    "groups_id": [(6, 0, [group_ids])],
                }
            )
        )

    @classmethod
    def _create_patient(cls):
        return cls.patient_model.create(
            {"name": "Test patient", "gender": "female"}
        )

    @classmethod
    def _create_payor(cls):
        return cls.payor_model.create({"name": "Test payor", "is_payor": True})

    @classmethod
    def _create_coverage_template(cls, state=False):
        vals = {"name": "test coverage template", "payor_id": cls.payor_1.id}
        if state:
            vals.update({"state": state})
        coverage_template = cls.coverage_template_model.create(vals)
        return coverage_template

    @classmethod
    def _create_coverage(cls, coverage_template, state=False, patient=False):
        vals = {
            "name": "test coverage",
            "patient_id": cls.patient_1.id,
            "coverage_template_id": coverage_template.id,
        }
        if state:
            vals.update({"state": state})
        if patient:
            vals.update({"patient_id": patient.id})
        coverage = cls.coverage_model.create(vals)
        return coverage

    @classmethod
    def _create_coverage_agreement_item(cls, coverage_agreement, product):
        return cls.coverage_agreement_model_item.create(
            {
                "coverage_agreement_id": coverage_agreement.id,
                "plan_definition_id": cls.plan_1.id,
                "product_id": product.id,
                "total_price": 100,
                "coverage_percentage": 100,
            }
        )

    @classmethod
    def _create_center(cls):
        return cls.center_model.create(
            {"name": "Test location", "is_center": True}
        )

    @classmethod
    def _create_product(cls, name):
        return cls.product_model.create(
            {
                "name": name,
                "categ_id": cls.env.ref("product.product_category_all").id,
                "type": "service",
            }
        )

    @classmethod
    def _create_type(cls):
        return cls.type_model.create(
            {
                "name": "Test type",
                "model_id": cls.env.ref(
                    "medical_administration.model_medical_patient"
                ).id,
                "model_ids": [
                    (
                        4,
                        cls.env.ref(
                            "medical_administration.model_medical_patient"
                        ).id,
                    )
                ],
            }
        )

    @classmethod
    def _create_act_def(cls):
        return cls.act_def_model.create(
            {
                "name": "Test activity",
                "model_id": cls.type_1.model_id.id,
                "service_id": cls.product_1.id,
            }
        )

    @classmethod
    def _create_action(cls):
        return cls.action_model.create(
            {
                "name": "Test action",
                "direct_plan_definition_id": cls.plan_1.id,
                "activity_definition_id": cls.act_def_1.id,
                "type_id": cls.type_1.id,
            }
        )

    @classmethod
    def _create_plan(cls):
        return cls.plan_model.create(
            {"name": "Test plan", "type_id": cls.type_1.id}
        )

    @classmethod
    def _create_coverage_agreement(cls, coverage_template):
        return cls.coverage_agreement_model.create(
            {
                "name": "test coverage agreement",
                "center_ids": [(6, 0, [cls.center_1.id])],
                "company_id": cls.env.ref("base.main_company").id,
                "coverage_template_ids": [(6, 0, coverage_template.ids)],
                "principal_concept": "coverage",
            }
        )

    def test_security(self):
        coverage_template = self._create_coverage_template()
        coverage_agreement_vals = {
            "name": "test coverage agreement",
            "center_ids": [(6, 0, [self.center_1.id])],
            "company_id": self.env.ref("base.main_company").id,
            "coverage_template_ids": [(6, 0, [coverage_template.id])],
        }
        coverage_agreement = self.coverage_agreement_model.with_user(
            self.medical_user
        ).create(coverage_agreement_vals)
        self.assertNotEquals(coverage_agreement, False)
        item_1 = self._create_coverage_agreement_item(
            coverage_agreement, self.product_1
        )
        coverage_agreement.action_search_item()
        self.assertEquals(item_1.coverage_price, 100)
        self.assertEquals(item_1.private_price, 0)

    def test_add_agreement_items_and_inactive(self):
        coverage_template = self._create_coverage_template()
        coverage_agreement = self._create_coverage_agreement(coverage_template)
        vals = {
            "coverage_agreement_id": coverage_agreement.id,
            "plan_definition_id": self.plan_1.id,
            "product_id": self.product_1.id,
            "total_price": 100,
        }
        self.coverage_agreement_model_item.create(vals)
        self.assertEquals(len(coverage_agreement.item_ids), 1)
        coverage_agreement.toggle_active()
        self.assertFalse(coverage_agreement.item_ids.active)

    def test_constrains_01(self):
        temp_01 = self._create_coverage_template()
        temp_02 = self._create_coverage_template()
        cent_01 = self._create_center()
        agr = self._create_coverage_agreement(temp_01)
        agr.write(
            {
                "center_ids": [(4, cent_01.id)],
                "coverage_template_ids": [(4, temp_02.id)],
            }
        )
        agr2 = self._create_coverage_agreement(temp_01)
        self._create_coverage_agreement_item(agr, self.product_1)
        with self.assertRaises(ValidationError):
            self._create_coverage_agreement_item(agr2, self.product_1)

    def test_constrains_02(self):
        temp_01 = self._create_coverage_template()
        temp_02 = self._create_coverage_template()
        cent_01 = self._create_center()
        agr = self._create_coverage_agreement(temp_01)
        agr2 = self._create_coverage_agreement(temp_02)
        self._create_coverage_agreement_item(agr, self.product_1)
        self._create_coverage_agreement_item(agr2, self.product_1)
        with self.assertRaises(ValidationError):
            agr.write(
                {
                    "center_ids": [(4, cent_01.id)],
                    "coverage_template_ids": [(4, temp_02.id)],
                }
            )

    def test_constrains_03(self):
        temp_01 = self._create_coverage_template()
        temp_02 = self._create_coverage_template()
        cent_01 = self._create_center()
        agr = self._create_coverage_agreement(temp_01)
        agr2 = self._create_coverage_agreement(temp_02)
        agr.write({"date_from": "2018-01-01", "date_to": "2018-01-31"})
        agr2.write({"date_from": "2018-02-01"})
        self._create_coverage_agreement_item(agr, self.product_1)
        self._create_coverage_agreement_item(agr2, self.product_1)
        agr.write(
            {
                "center_ids": [(4, cent_01.id)],
                "coverage_template_ids": [(4, temp_02.id)],
            }
        )
        with self.assertRaises(ValidationError):
            agr2.write({"date_from": "2018-01-31"})

    def test_constrains_04(self):
        temp_01 = self._create_coverage_template()
        temp_02 = self._create_coverage_template()
        cent_01 = self._create_center()
        agr = self._create_coverage_agreement(temp_01)
        agr2 = self._create_coverage_agreement(temp_02)
        agr.write({"date_from": "2018-01-01", "date_to": "2018-01-31"})
        agr2.write({"date_from": "2018-02-01"})
        self._create_coverage_agreement_item(agr, self.product_1)
        self._create_coverage_agreement_item(agr2, self.product_1)
        agr.write(
            {
                "center_ids": [(4, cent_01.id)],
                "coverage_template_ids": [(4, temp_02.id)],
            }
        )
        with self.assertRaises(ValidationError):
            agr.write({"date_to": "2018-02-01"})

    def test_change_prices(self):
        # case 1
        coverage_agreement_vals = {
            "name": "test coverage agreement",
            "center_ids": [(6, 0, [self.center_1.id])],
            "company_id": self.ref("base.main_company"),
        }
        coverage_agreement = self.coverage_agreement_model.create(
            coverage_agreement_vals
        )
        self.assertNotEquals(coverage_agreement, False)
        item_1 = self.coverage_agreement_model_item.create(
            {
                "coverage_agreement_id": coverage_agreement.id,
                "plan_definition_id": self.plan_1.id,
                "product_id": self.product_1.id,
                "coverage_percentage": 50.0,
                "total_price": 200,
            }
        )
        self.assertEquals(item_1.coverage_price, 100)
        self.assertEquals(item_1.private_price, 100)
        wiz = self.env["medical.agreement.change.prices"].create(
            {"difference": 50.0}
        )
        wiz.with_context(active_ids=[coverage_agreement.id]).change_prices()
        item_1.refresh()
        self.assertEquals(item_1.coverage_price, 150)
        self.assertEquals(item_1.private_price, 150)

    def test_agreement_report(self):

        coverage_agreement_vals = {
            "name": "test coverage agreement",
            "center_ids": [(6, 0, [self.center_1.id])],
            "company_id": self.ref("base.main_company"),
        }
        coverage_agreement = self.coverage_agreement_model.create(
            coverage_agreement_vals
        )
        self.assertNotEquals(coverage_agreement, False)
        item = self.coverage_agreement_model_item.create(
            {
                "coverage_agreement_id": coverage_agreement.id,
                "plan_definition_id": self.plan_1.id,
                "product_id": self.product_1.id,
                "coverage_percentage": 100.0,
                "total_price": 200,
            }
        )
        data = coverage_agreement._agreement_report_data(False)
        self.assertFalse(data)
        data = coverage_agreement._agreement_report_data()
        self.assertTrue(data)
        self.assertEqual(
            data[0]["category"], self.env.ref("product.product_category_all"),
        )
        self.assertFalse(data[0]["childs"])
        self.assertEqual(item, data[0]["data"][0]["item"])
        self.assertFalse(data[0]["data"][0]["nomenclature"])
        category = self.env["product.category"].create(
            {
                "parent_id": self.env.ref("product.product_category_all").id,
                "name": "Categ",
            }
        )
        self.product_1.categ_id = category
        data = coverage_agreement._agreement_report_data()
        self.assertTrue(data)
        self.assertEqual(
            data[0]["category"], self.env.ref("product.product_category_all"),
        )
        self.assertTrue(data[0]["childs"])
        self.assertFalse(data[0]["data"])
        self.assertEqual(data[0]["childs"][0]["category"], category)
        self.assertEqual(item, data[0]["childs"][0]["data"][0]["item"])
        self.assertFalse(data[0]["childs"][0]["data"][0]["nomenclature"])
        nomenclature = self.env["product.nomenclature"].create(
            {
                "name": "NOMENC",
                "code": "NOMENC",
                "item_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_1.id,
                            "code": "test",
                            "name": "test",
                        },
                    )
                ],
            }
        )
        coverage_agreement.nomenclature_id = nomenclature
        data = coverage_agreement._agreement_report_data()
        self.assertTrue(data[0]["childs"])
        self.assertFalse(data[0]["data"])
        self.assertEqual(data[0]["childs"][0]["category"], category)
        self.assertEqual(item, data[0]["childs"][0]["data"][0]["item"])
        self.assertEqual(
            nomenclature.item_ids,
            data[0]["childs"][0]["data"][0]["nomenclature"],
        )

    def test_export_xslx(self):
        coverage_agreement_vals = {
            "name": "test coverage agreement",
            "center_ids": [(6, 0, [self.center_1.id])],
            "company_id": self.ref("base.main_company"),
        }
        coverage_agreement = self.coverage_agreement_model.create(
            coverage_agreement_vals
        )
        item = self.coverage_agreement_model_item.create(
            {
                "coverage_agreement_id": coverage_agreement.id,
                "plan_definition_id": self.plan_1.id,
                "product_id": self.product_1.id,
                "coverage_percentage": 50.0,
                "total_price": 200,
            }
        )

        report_object = self.env["ir.actions.report"]
        report_name = "medical_financial_coverage_agreement.items_xslx"
        report = report_object._get_report_from_name(report_name)

        rep = report.render(item.ids)
        sheet = pandas.read_excel(BytesIO(rep[0]), engine="openpyxl")
        self.assertEqual(sheet[sheet.columns[1]][0], item.product_id.name)

        category_2 = self.env["product.category"].create(
            {
                "name": "Categ 2",
                "parent_id": self.env.ref("product.product_category_all").id,
            }
        )
        product_2 = self.product_model.create(
            {"name": "Product 2", "categ_id": category_2.id}
        )
        self.coverage_agreement_model_item.create(
            {
                "coverage_agreement_id": coverage_agreement.id,
                "plan_definition_id": self.plan_1.id,
                "product_id": product_2.id,
                "coverage_percentage": 0,
                "total_price": 200,
            }
        )

        report_name = "medical_financial_coverage_agreement.mca_xlsx_private"
        report = report_object._get_report_from_name(report_name)

        rep = report.with_context(
            active_model="medical.coverage.agreement", xlsx_private=True
        ).render(coverage_agreement.ids)
        sheet = pandas.read_excel(BytesIO(rep[0]), engine="openpyxl")
        self.assertEqual(
            sheet.columns[0],
            self.env.ref("product.product_category_all").name,
        )
        self.assertEqual(sheet[sheet.columns[2]][0], self.product_1.name)
        self.assertEqual(sheet[sheet.columns[1]][1], category_2.display_name)
        self.assertEqual(sheet[sheet.columns[3]][2], product_2.name)

    def test_join_agreements(self):
        temp_01 = self._create_coverage_template()
        agr = self._create_coverage_agreement(temp_01)
        agr2 = self._create_coverage_agreement(temp_01)
        self._create_coverage_agreement_item(agr, self.product_1)
        self._create_coverage_agreement_item(agr2, self.product_2)
        (agr | agr2).write(
            {
                "center_ids": [(4, self.center_1.id)],
                "coverage_template_ids": [(4, temp_01.id)],
            }
        )
        self.env["medical.coverage.agreement.join"].with_context(
            active_model=(agr | agr2)._name, active_ids=(agr | agr2).ids,
        ).create({}).run()
        joined = (agr | agr2).filtered(lambda r: r.item_ids)
        self.assertEqual(len(joined), 1)
        self.assertEqual(len(joined.item_ids), 2)

    def test_join_agreements_constrain_01(self):
        temp_01 = self._create_coverage_template()
        agr = self._create_coverage_agreement(temp_01)
        agr2 = self._create_coverage_agreement(self.coverage_template_1)
        self._create_coverage_agreement_item(agr, self.product_1)
        self._create_coverage_agreement_item(agr2, self.product_2)
        (agr | agr2).write({"center_ids": [(4, self.center_1.id)]})
        with self.assertRaises(ValidationError):
            self.env["medical.coverage.agreement.join"].with_context(
                active_model=(agr | agr2)._name, active_ids=(agr | agr2).ids,
            ).create({}).run()

    def test_join_agreements_constrain_02(self):
        temp_01 = self._create_coverage_template()
        agr = self._create_coverage_agreement(temp_01)
        agr2 = self._create_coverage_agreement(temp_01)
        self._create_coverage_agreement_item(agr, self.product_1)
        self._create_coverage_agreement_item(agr2, self.product_2)
        agr2.center_ids = self.center_1
        agr.center_ids = self._create_center()
        with self.assertRaises(ValidationError):
            self.env["medical.coverage.agreement.join"].with_context(
                active_model=(agr | agr2)._name, active_ids=(agr | agr2).ids,
            ).create({}).run()

    def test_join_agreements_constrain_03(self):
        temp_01 = self._create_coverage_template()
        agr = self._create_coverage_agreement(temp_01)
        self._create_coverage_agreement_item(agr, self.product_1)
        agr.center_ids = self._create_center()
        with self.assertRaises(ValidationError):
            self.env["medical.coverage.agreement.join"].with_context(
                active_model=agr._name, active_ids=agr.ids,
            ).create({}).run()

    def test_join_agreements_constrain_04(self):
        temp_01 = self._create_coverage_template()
        agr = self._create_coverage_agreement(temp_01)
        agr2 = self._create_coverage_agreement(temp_01)
        self._create_coverage_agreement_item(agr, self.product_1)
        self._create_coverage_agreement_item(agr2, self.product_2)
        (agr | agr2).write(
            {
                "center_ids": [(4, self.center_1.id)],
                "coverage_template_ids": [(4, temp_01.id)],
            }
        )
        agr.company_id = self.env["res.company"].create(
            {"name": "Demo company"}
        )
        with self.assertRaises(ValidationError):
            self.env["medical.coverage.agreement.join"].with_context(
                active_model=(agr | agr2)._name, active_ids=(agr | agr2).ids,
            ).create({}).run()

    def test_template_constrain_01(self):
        temp_01 = self._create_coverage_agreement(
            self.env["medical.coverage.template"]
        )
        temp_01.is_template = True
        with self.assertRaises(ValidationError):
            temp_01.coverage_template_ids = self.coverage_template_1

    def test_template_constrain_02(self):
        temp_01 = self._create_coverage_agreement(
            self.env["medical.coverage.template"]
        )
        temp_01.is_template = True
        temp_02 = self._create_coverage_agreement(
            self.env["medical.coverage.template"]
        )
        temp_02.is_template = True
        with self.assertRaises(ValidationError):
            self.env["medical.coverage.agreement.template"].create(
                {
                    "agreement_id": temp_02.id,
                    "template_id": temp_01.id,
                    "set_items": True,
                }
            ).run()

    def test_template_wizard(self):
        temp_01 = self._create_coverage_agreement(
            self.env["medical.coverage.template"]
        )
        temp_01.is_template = True
        self._create_coverage_agreement_item(temp_01, self.product_1)
        self._create_coverage_agreement_item(temp_01, self.product_2)

        aggr = self._create_coverage_agreement(self.coverage_template_1)
        self.assertFalse(aggr.item_ids)
        self.env["medical.coverage.agreement.template"].create(
            {
                "agreement_id": aggr.id,
                "template_id": temp_01.id,
                "set_items": True,
            }
        ).run()
        self.assertTrue(aggr.item_ids)
        self.assertEqual(len(aggr.item_ids), 2)
        self.assertEqual(aggr.template_id, temp_01)

    def test_template_wizard_no_items(self):
        temp_01 = self._create_coverage_agreement(
            self.env["medical.coverage.template"]
        )
        temp_01.is_template = True
        self._create_coverage_agreement_item(temp_01, self.product_1)
        self._create_coverage_agreement_item(temp_01, self.product_2)

        aggr = self._create_coverage_agreement(self.coverage_template_1)
        self.assertFalse(aggr.item_ids)
        self.env["medical.coverage.agreement.template"].create(
            {"agreement_id": aggr.id, "template_id": temp_01.id}
        ).run()
        self.assertFalse(aggr.item_ids)
        self.assertEqual(aggr.template_id, temp_01)

    def test_agreement_line_onchange(self):
        aggr_01 = self._create_coverage_agreement(
            self.env["medical.coverage.template"]
        )
        aggr_01.principal_concept = "private"
        self.product_1.agreement_comment = "MY COMMENT"
        with Form(
            self.env["medical.coverage.agreement.item"].with_context(
                default_coverage_agreement_id=aggr_01.id
            )
        ) as item:
            item.product_id = self.product_1
            self.assertEqual(item.coverage_percentage, 0)
            self.assertEqual(item.item_comment, "MY COMMENT")

    def test_agreement_line_onchange_template(self):
        aggr_01 = self._create_coverage_agreement(
            self.env["medical.coverage.template"]
        )
        temp_01 = self._create_coverage_agreement(
            self.env["medical.coverage.template"]
        )
        temp_01.is_template = True
        self._create_coverage_agreement_item(temp_01, self.product_1)
        self.env["medical.coverage.agreement.template"].create(
            {
                "agreement_id": aggr_01.id,
                "template_id": temp_01.id,
                "set_items": False,
            }
        ).run()
        with Form(
            self.env["medical.coverage.agreement.item"].with_context(
                default_coverage_agreement_id=aggr_01.id
            )
        ) as item:
            item.product_id = self.product_1
            self.assertEqual(100, item.total_price)
            self.assertEqual(item.plan_definition_id, self.plan_1)

    def test_agreement_line_constrain(self):
        aggr_01 = self._create_coverage_agreement(
            self.env["medical.coverage.template"]
        )
        self._create_coverage_agreement_item(aggr_01, self.product_1)
        with self.assertRaises(ValidationError):
            self._create_coverage_agreement_item(aggr_01, self.product_1)

    def test_search(self):
        aggr_01 = self._create_coverage_agreement(
            self.env["medical.coverage.template"]
        )
        self.product_1.default_code = "DEMO DEFAULT CODE"
        self.product_1.name = "DEMO DEFAULT NAME"
        self._create_coverage_agreement_item(aggr_01, self.product_1)
        self.assertEqual(
            aggr_01.item_ids.name_get(),
            self.coverage_agreement_model_item._name_search(
                "DEMO DEFAULT CODE",
                [("coverage_agreement_id", "=", aggr_01.id)],
            ),
        )
        self.assertEqual(
            aggr_01.item_ids.name_get(),
            self.coverage_agreement_model_item._name_search(
                "DEMO DEFAULT NAME",
                [("coverage_agreement_id", "=", aggr_01.id)],
            ),
        )
