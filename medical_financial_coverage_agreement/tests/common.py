from odoo.tests.common import SavepointCase


class AgrementSavepointCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.medical_user_group = cls.env.ref("medical_base.group_medical_configurator")
        cls.medical_financial_group = cls.env.ref(
            "medical_base.group_medical_financial"
        )
        cls.medical_user = cls._create_user(
            "group_medical_user", cls.medical_user_group.id
        )
        cls.medical_user.groups_id |= cls.medical_financial_group
        cls.patient_model = cls.env["medical.patient"]
        cls.coverage_model = cls.env["medical.coverage"]
        cls.coverage_template_model = cls.env["medical.coverage.template"]
        cls.payor_model = cls.env["res.partner"]
        cls.coverage_agreement_model = cls.env["medical.coverage.agreement"]
        cls.coverage_agreement_model_item = cls.env["medical.coverage.agreement.item"]
        cls.center_model = cls.env["res.partner"]
        cls.product_model = cls.env["product.product"]
        # cls.type_model = cls.env["workflow.type"]
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
        # cls.type_1 = cls._create_type()
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
        return cls.patient_model.create({"name": "Test patient", "gender": "female"})

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
            cls._create_coverage_agreement_item_vals(coverage_agreement, product)
        )

    @classmethod
    def _create_coverage_agreement_item_vals(cls, coverage_agreement, product):
        return {
            "coverage_agreement_id": coverage_agreement.id,
            "plan_definition_id": cls.plan_1.id,
            "product_id": product.id,
            "total_price": 100,
            "coverage_percentage": 100,
        }

    @classmethod
    def _create_center(cls):
        return cls.center_model.create({"name": "Test location", "is_center": True})

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
    def _create_act_def(cls):
        return cls.act_def_model.create(
            {
                "name": "Test activity",
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
            }
        )

    @classmethod
    def _create_plan(cls):
        return cls.plan_model.create(
            {
                "name": "Test plan",
            }
        )

    @classmethod
    def _create_coverage_agreement(cls, coverage_template):
        return cls.coverage_agreement_model.create(
            cls._create_coverage_agreement_vals(coverage_template)
        )

    @classmethod
    def _create_coverage_agreement_vals(cls, coverage_template):
        return {
            "name": "test coverage agreement",
            "center_ids": [(6, 0, [cls.center_1.id])],
            "company_id": cls.env.ref("base.main_company").id,
            "coverage_template_ids": [(6, 0, coverage_template.ids)],
            "principal_concept": "coverage",
        }
