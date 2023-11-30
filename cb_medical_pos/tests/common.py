from odoo.addons.cb_medical_careplan_sale.tests import common


class MedicalSavePointCase(common.MedicalSavePointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_2 = cls.env["res.company"].create({"name": "New company"})
        cls.company_2 = cls.env["res.company"].create(
            {
                "name": "New Company",
            }
        )
        cls.env.user.company_ids |= cls.company_2
        cls.env.company.chart_template_id.try_loading(company=cls.company_2)
        cls.bank_account_2 = cls.env["account.account"].create(
            {
                "name": "Bank account",
                "code": "5720BNK",
                "company_id": cls.company_2.id,
                "currency_id": cls.company_2.currency_id.id,
                "user_type_id": cls.env.ref("account.data_account_type_liquidity").id,
            }
        )
        cls.payment_method_2 = cls.env["pos.payment.method"].create(
            {
                "name": "Payment method test",
                "receivable_account_id": cls.bank_account_2.id,
                "company_id": cls.company_2.id,
            }
        )
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
            .default_get(
                [
                    "stock_location_id",
                    "invoice_journal_id",
                    "pricelist_id",
                    "journal_id",
                ]
            )
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
        pos_vals = (
            cls.env["pos.config"]
            .with_company(cls.company_2.id)
            .default_get(
                [
                    "stock_location_id",
                    "invoice_journal_id",
                    "pricelist_id",
                    "journal_id",
                ]
            )
        )
        pos_vals.update(
            {
                "name": "Config",
                "payment_method_ids": cls.payment_method_2,
                "requires_approval": True,
                "company_id": cls.company_2.id,
                "crm_team_id": False,
                "journal_id": cls.env["account.journal"]
                .create(
                    {
                        "name": "PoS Journal",
                        "code": "SALES",
                        "company_id": cls.company_2.id,
                        "type": "sale",
                    }
                )
                .id,
            }
        )
        cls.pos_config_2 = (
            cls.env["pos.config"].with_company(cls.company_2.id).create(pos_vals)
        )
        cls.pos_config_2.open_session_cb()
        cls.pos_config.current_session_id.action_pos_session_open()
        cls.session_2 = cls.pos_config_2.current_session_id
        cls.def_third_party_product = cls.create_product("THIRD PARTY PRODUCT")
        cls.env["ir.config_parameter"].set_param(
            "cb.default_third_party_product", cls.def_third_party_product.id
        )
        cls.company.deposit_account_id = cls.env["account.account"].create(
            {
                "company_id": cls.company.id,
                "code": "DepositAcc",
                "name": "Deposit account",
                "user_type_id": cls.env.ref("account.data_account_type_receivable").id,
                "reconcile": True,
            }
        )
        cls.company.patient_journal_id = cls.env["account.journal"].create(
            {
                "name": "Sale Journal",
                "code": "SALES",
                "company_id": cls.company.id,
                "type": "sale",
            }
        )
        cls.company.deposit_journal_id = cls.env["account.journal"].create(
            {
                "name": "Deposit Journal",
                "code": "DEPOSIT",
                "company_id": cls.company.id,
                "type": "general",
            }
        )
        cls.company_2.deposit_account_id = cls.env["account.account"].create(
            {
                "company_id": cls.company_2.id,
                "code": "DepositAcc",
                "name": "Deposit account",
                "user_type_id": cls.env.ref("account.data_account_type_receivable").id,
                "reconcile": True,
            }
        )
        cls.company_2.patient_journal_id = cls.env["account.journal"].create(
            {
                "name": "Sale Journal",
                "code": "SALES",
                "company_id": cls.company_2.id,
                "type": "sale",
            }
        )
        cls.company_2.deposit_journal_id = cls.env["account.journal"].create(
            {
                "name": "Deposit Journal",
                "code": "DEPOSIT",
                "company_id": cls.company_2.id,
                "type": "general",
            }
        )

    @classmethod
    def create_inter_company(
        cls, company_1, company_2, journal_1=False, journal_2=False
    ):
        journal_obj = cls.env["account.journal"]
        if not journal_1:
            account = cls.env["account.account"].create(
                {
                    "name": "Intercompany to %s" % company_2.name,
                    "code": "I;%s" % company_2.id,
                    "company_id": company_1.id,
                    "user_type_id": cls.env.ref(
                        "account.data_account_type_liquidity"
                    ).id,
                }
            )
            journal_1 = journal_obj.create(
                {
                    "name": "Journal from %s to %s" % (company_1.name, company_2.name),
                    "code": "I;{};{}".format(company_1.id, company_2.id),
                    "type": "general",
                    "company_id": company_1.id,
                    "default_account_id": account.id,
                }
            )
        if not journal_2:
            account = cls.env["account.account"].create(
                {
                    "name": "Intercompany to %s" % company_1.name,
                    "code": "I;%s" % company_1.id,
                    "company_id": company_2.id,
                    "user_type_id": cls.env.ref(
                        "account.data_account_type_liquidity"
                    ).id,
                }
            )
            journal_2 = journal_obj.create(
                {
                    "name": "Journal from %s to %s" % (company_2.name, company_1.name),
                    "code": "I;{};{}".format(company_2.id, company_1.id),
                    "type": "general",
                    "company_id": company_2.id,
                    "default_account_id": account.id,
                }
            )
        cls.env["res.inter.company"].create(
            {
                "company_id": company_1.id,
                "related_company_id": company_2.id,
                "journal_id": journal_1.id,
                "related_journal_id": journal_2.id,
            }
        )
