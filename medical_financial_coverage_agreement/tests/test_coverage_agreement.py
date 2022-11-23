# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import logging
from datetime import timedelta
from io import BytesIO

import pandas

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import Form

from ..tests import common

_logger = logging.getLogger(__name__)


class TestMedicalCoverageAgreement(common.AgrementSavepointCase):
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
        self.assertEqual(item_1.coverage_price, 100)
        self.assertEqual(item_1.private_price, 0)

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
        self.assertEqual(len(coverage_agreement.item_ids), 1)
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
        self.assertEqual(item_1.coverage_price, 100)
        self.assertEqual(item_1.private_price, 100)
        wiz = self.env["medical.agreement.change.prices"].create({"difference": 50.0})
        wiz.with_context(active_ids=[coverage_agreement.id]).change_prices()
        item_1.refresh()
        self.assertEqual(item_1.coverage_price, 150)
        self.assertEqual(item_1.private_price, 150)

    def test_expand(self):
        # case 1
        coverage_agreement_vals = {
            "name": "test coverage agreement",
            "center_ids": [(6, 0, [self.center_1.id])],
            "company_id": self.ref("base.main_company"),
            "date_to": fields.Date.today(),
            "coverage_template_ids": [(4, self.coverage_template_1.id)],
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
        self.assertEqual(item_1.coverage_price, 100)
        self.assertEqual(item_1.private_price, 100)
        wiz = (
            self.env["medical.agreement.expand"]
            .with_context(
                default_agreement_id=coverage_agreement.id,
                default_name=coverage_agreement.name,
            )
            .create(
                {
                    "difference": 50.0,
                    "date_to": fields.Date.today() + timedelta(days=1),
                }
            )
        )
        action = wiz.expand()
        item_1.refresh()
        self.assertEqual(item_1.coverage_price, 100)
        self.assertEqual(item_1.private_price, 100)
        new_agreement = self.env[action["res_model"]].browse(action["res_id"])
        self.assertEqual(
            new_agreement.coverage_template_ids,
            coverage_agreement.coverage_template_ids,
        )
        new_item_1 = new_agreement.item_ids.filtered(
            lambda r: r.product_id == self.product_1
        )
        self.assertEqual(new_item_1.coverage_price, 150)
        self.assertEqual(new_item_1.private_price, 150)

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
            data[0]["category"],
            self.env.ref("product.product_category_all"),
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
            data[0]["category"],
            self.env.ref("product.product_category_all"),
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
            active_model=(agr | agr2)._name,
            active_ids=(agr | agr2).ids,
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
                active_model=(agr | agr2)._name,
                active_ids=(agr | agr2).ids,
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
                active_model=(agr | agr2)._name,
                active_ids=(agr | agr2).ids,
            ).create({}).run()

    def test_join_agreements_constrain_03(self):
        temp_01 = self._create_coverage_template()
        agr = self._create_coverage_agreement(temp_01)
        self._create_coverage_agreement_item(agr, self.product_1)
        agr.center_ids = self._create_center()
        with self.assertRaises(ValidationError):
            self.env["medical.coverage.agreement.join"].with_context(
                active_model=agr._name,
                active_ids=agr.ids,
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
        agr.company_id = self.env["res.company"].create({"name": "Demo company"})
        with self.assertRaises(ValidationError):
            self.env["medical.coverage.agreement.join"].with_context(
                active_model=(agr | agr2)._name,
                active_ids=(agr | agr2).ids,
            ).create({}).run()

    def test_template_constrain_01(self):
        temp_01 = self._create_coverage_agreement(self.env["medical.coverage.template"])
        temp_01.is_template = True
        with self.assertRaises(ValidationError):
            temp_01.coverage_template_ids = self.coverage_template_1

    def test_template_constrain_02(self):
        temp_01 = self._create_coverage_agreement(self.env["medical.coverage.template"])
        temp_01.is_template = True
        temp_02 = self._create_coverage_agreement(self.env["medical.coverage.template"])
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
        temp_01 = self._create_coverage_agreement(self.env["medical.coverage.template"])
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
        temp_01 = self._create_coverage_agreement(self.env["medical.coverage.template"])
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
        aggr_01 = self._create_coverage_agreement(self.env["medical.coverage.template"])
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
        aggr_01 = self._create_coverage_agreement(self.env["medical.coverage.template"])
        temp_01 = self._create_coverage_agreement(self.env["medical.coverage.template"])
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
        aggr_01 = self._create_coverage_agreement(self.env["medical.coverage.template"])
        self._create_coverage_agreement_item(aggr_01, self.product_1)
        with self.assertRaises(ValidationError):
            self._create_coverage_agreement_item(aggr_01, self.product_1)

    def test_search(self):
        aggr_01 = self._create_coverage_agreement(self.env["medical.coverage.template"])
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
