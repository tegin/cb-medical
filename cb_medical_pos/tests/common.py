from odoo.addons.cb_medical_careplan_sale.tests import common


class MedicalSavePointCase(common.MedicalSavePointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.reina = cls.env["res.partner"].create(
            {
                "name": "Reina",
                "is_medical": True,
                "is_center": True,
                "encounter_sequence_prefix": "9",
            }
        )
        cls.payment_method_id = cls.env["pos.payment.method"].create(
            {
                "name": "Payment method test",
                "receivable_account_id": cls.bank_account.id,
            }
        )
        pos_vals = (
            cls.env["pos.config"]
            .with_context(company_id=cls.company.id)
            .default_get(["stock_location_id", "invoice_journal_id", "pricelist_id"])
        )
        pos_vals.update(
            {
                "name": "Config",
                "payment_method_ids": cls.payment_method_id,
                "requires_approval": True,
                "company_id": cls.company.id,
                "crm_team_id": False,
            }
        )
        cls.pos_config = cls.env["pos.config"].create(pos_vals)
        cls.pos_config.open_session_cb()
        cls.session = cls.pos_config.current_session_id
        cls.session.action_pos_session_open()
        cls.def_third_party_product = cls.create_product("THIRD PARTY PRODUCT")
        cls.env["ir.config_parameter"].set_param(
            "cb.default_third_party_product", cls.def_third_party_product.id
        )
        cls.company.patient_journal_id = cls.env["account.journal"].create(
            {
                "name": "Sale Journal",
                "code": "SALES",
                "company_id": cls.company.id,
                "type": "sale",
            }
        )
