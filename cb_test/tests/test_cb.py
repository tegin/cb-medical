# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from dateutil.relativedelta import relativedelta
import base64
from datetime import timedelta
from odoo import fields
from odoo.tests.common import SavepointCase
from odoo.exceptions import UserError, ValidationError
from mock import patch


class TestMedicalCareplanSale(SavepointCase):
    def setUp(self):
        super().setUp()
        name = 'testing_remote_server'
        self.remote = self.env['res.remote'].search([('name', '=', name)])
        if not self.remote:
            self.remote = self.env['res.remote'].create({
                'name': name,
                'ip': '127.0.0.1',
            })
        self.server = self.env['printing.server'].create({
            'name': 'Server',
            'address': 'localhost',
            'port': 631,
        })
        self.printer = self.env['printing.printer'].create({
            'name': 'Printer 1',
            'system_name': 'P1',
            'server_id': self.server.id,
        })
        self.env['res.remote.printer'].create({
            'remote_id': self.remote.id,
            'printer_id': self.printer.id,
            'is_default': True,
        })
        self.env['res.remote.printer'].create({
            'remote_id': self.remote.id,
            'printer_id': self.printer.id,
            'is_default': True,
            'printer_usage': 'label',
        })
        self.nomenclature = self.env['product.nomenclature'].create({
            'name': 'Nomenclature',
            'code': 'nomenc',
        })
        self.payor = self.env['res.partner'].create({
            'name': 'Payor',
            'is_payor': True,
            'is_medical': True,
            'invoice_nomenclature_id': self.nomenclature.id,
        })
        self.sub_payor = self.env['res.partner'].create({
            'name': 'Sub Payor',
            'is_sub_payor': True,
            'is_medical': True,
            'payor_id': self.payor.id,
        })
        self.coverage_template = self.env['medical.coverage.template'].create({
            'payor_id': self.payor.id,
            'name': 'Coverage',
        })
        self.coverage_template_2 = self.env[
            'medical.coverage.template'
        ].create({
            'payor_id': self.payor.id,
            'name': 'Coverage 2',
        })
        self.company = self.browse_ref('base.main_company')
        self.company.patient_journal_id = self.env['account.journal'].create({
            'name': 'Sale Journal',
            'code': 'SALES',
            'company_id': self.company.id,
            'type': 'sale',
        })
        self.company.third_party_journal_id = self.env[
            'account.journal'
        ].create({
            'name': 'Journal',
            'code': 'THIRD',
            'company_id': self.company.id,
            'type': 'general',
        })
        self.customer_acc = self.env['account.account'].create({
            'company_id': self.company.id,
            'code': 'ThirdPartyCust',
            'name': 'Third party customer account',
            'user_type_id': self.browse_ref(
                'account.data_account_type_receivable').id,
            'reconcile': True,
        })
        self.supplier_acc = self.env['account.account'].create({
            'company_id': self.company.id,
            'code': 'ThirdPartySupp',
            'name': 'Third party supplier account',
            'user_type_id': self.browse_ref(
                'account.data_account_type_payable').id,
            'reconcile': True,
        })
        self.company.write({
            'default_third_party_customer_account_id': self.customer_acc.id,
            'default_third_party_supplier_account_id': self.supplier_acc.id,
        })
        self.tax = self.env['account.tax'].create({
            'name': 'TAX',
            'amount_type': 'percent',
            'amount': 0,
            'type_tax_use': 'sale',
            'company_id': self.company.id,
        })
        self.center = self.env['res.partner'].create({
            'name': 'Center',
            'is_medical': True,
            'is_center': True,
            'encounter_sequence_prefix': 'S',
        })
        self.location = self.env['res.partner'].create({
            'name': 'Location',
            'is_medical': True,
            'is_location': True,
            'center_id': self.center.id,
            'stock_location_id': self.browse_ref('stock.warehouse0').id,
            'stock_picking_type_id': self.env['stock.picking.type'].search(
                [], limit=1).id
        })
        self.document_type = self.env['medical.document.type'].create({
            'name': 'CI',
            'document_type': 'action',
            'report_action_id': self.browse_ref(
                'medical_document.action_report_document_report_base').id,
        })
        self.lang_es = self.browse_ref('base.lang_es')
        if not self.lang_es.active:
            self.lang_es.toggle_active()
        self.lang_en = self.browse_ref('base.lang_en')
        if not self.lang_en.active:
            self.lang_en.toggle_active()
        self.env['medical.document.type.lang'].create({
            'lang': self.lang_es.code,
            'document_type_id': self.document_type.id,
            'text': '<p>%s</p><p>${object.patient_id.name}'
                    '</p>' % self.lang_es.code
        })
        self.env['medical.document.type.lang'].create({
            'lang': self.lang_en.code,
            'document_type_id': self.document_type.id,
            'text': '<p>%s</p><p>${object.patient_id.name}'
                    '</p>' % self.lang_en.code
        })
        self.label_zpl2 = self.env['printing.label.zpl2'].create({
            'name': 'Label',
            'model_id': self.browse_ref(
                'medical_document.model_medical_document_reference').id,
            'component_ids': [(0, 0, {
                'name': 'text',
                'component_type': 'text',
                'data': 'object.encounter_id.internal_identifier',
                'origin_x': 10,
                'origin_y': 10,
                'height': 10,
                'width': 10,
                'font': '0',
                'orientation': 'N',

            })]
        })
        self.document_type.draft2current()
        self.document_type_label = self.env['medical.document.type'].create({
            'name': 'Label for scan',
            'document_type': 'zpl2',
            'label_zpl2_id': self.label_zpl2.id,
        })
        self.document_type_label.draft2current()
        self.agreement = self.env['medical.coverage.agreement'].create({
            'name': 'Agreement',
            'center_ids': [(4, self.center.id)],
            'coverage_template_ids': [(4, self.coverage_template.id)],
            'company_id': self.company.id,
            'invoice_group_method_id': self.browse_ref(
                'cb_medical_sale_invoice_group_method.by_preinvoicing').id,
            'authorization_method_id': self.browse_ref(
                'cb_medical_financial_coverage_request.without').id,
            'authorization_format_id': self.browse_ref(
                'cb_medical_financial_coverage_request.format_anything').id,
        })
        self.format = self.env['medical.authorization.format'].create({
            'code': 'TEST',
            'name': 'test',
            'authorization_format': '^1.*$'
        })
        self.patient_01 = self.create_patient('Patient 01')
        self.coverage_01 = self.env['medical.coverage'].create({
            'patient_id': self.patient_01.id,
            'coverage_template_id': self.coverage_template.id,
        })
        self.coverage_02 = self.env['medical.coverage'].create({
            'patient_id': self.patient_01.id,
            'coverage_template_id': self.coverage_template_2.id,
        })
        self.product_01 = self.create_product('Medical resonance')
        self.product_02 = self.create_product('Report')
        self.service = self.env['product.product'].create({
            'name': 'Service',
            'type': 'service',
            'taxes_id': [(6, 0, self.tax.ids)],
        })
        self.category = self.env['product.category'].create({
            'name': 'Category',
            'category_product_id': self.service.id,
        })
        self.product_03 = self.env['product.product'].create({
            'type': 'consu',
            'categ_id': self.category.id,
            'name': 'Clinical material',
            'is_medication': True,
            'lst_price': 10.0,
            'taxes_id': [(6, 0, self.tax.ids)],
        })
        self.product_03.qty_available = 50.0
        self.product_04 = self.create_product('Medical visit')
        self.lab_product = self.create_product('Laboratory Product')
        self.type = self.browse_ref('medical_workflow.medical_workflow')
        self.type.model_ids = [(4, self.browse_ref(
            'medical_medication_request.model_medical_medication_request').id)]
        self.plan_definition = self.env['workflow.plan.definition'].create({
            'name': 'Plan',
            'type_id': self.type.id,
            'is_billable': True,
        })
        self.plan_definition.activate()
        self.plan_definition2 = self.env['workflow.plan.definition'].create({
            'name': 'Plan2',
            'type_id': self.type.id,
            'is_billable': True,
            'is_breakdown': False,
            'third_party_bill': True,
        })
        self.plan_definition2.activate()
        self.plan_definition3 = self.env['workflow.plan.definition'].create({
            'name': 'Plan2',
            'type_id': self.type.id,
            'is_billable': True,
            'is_breakdown': False,
            'third_party_bill': False,
        })
        self.plan_definition3.activate()
        self.activity = self.env['workflow.activity.definition'].create({
            'name': 'Activity',
            'service_id': self.product_02.id,
            'model_id': self.browse_ref('medical_clinical_procedure.'
                                        'model_medical_procedure_request').id,
            'type_id': self.type.id,
        })
        self.activity.activate()
        self.activity2 = self.env['workflow.activity.definition'].create({
            'name': 'Activity2',
            'service_id': self.service.id,
            'model_id': self.browse_ref('medical_medication_request.'
                                        'model_medical_medication_request').id,
            'type_id': self.type.id,
        })
        self.activity2.activate()
        self.activity3 = self.env['workflow.activity.definition'].create({
            'name': 'Activity3',
            'model_id': self.browse_ref(
                'medical_document.model_medical_document_reference').id,
            'document_type_id': self.document_type.id,
            'type_id': self.type.id,
        })
        self.activity3.activate()
        self.activity4 = self.env['workflow.activity.definition'].create({
            'name': 'Activity4',
            'model_id': self.browse_ref(
                'medical_document.model_medical_document_reference').id,
            'document_type_id': self.document_type_label.id,
            'type_id': self.type.id,
        })
        self.activity4.activate()
        self.activity5 = self.env['workflow.activity.definition'].create({
            'name': 'Activity 5',
            'service_id': self.product_02.id,
            'model_id': self.browse_ref('medical_clinical_procedure.'
                                        'model_medical_procedure_request').id,
            'type_id': self.type.id,
        })
        self.activity5.activate()
        self.lab_activity = self.env['workflow.activity.definition'].create({
            'name': 'Laboratory activity',
            'service_id': self.product_02.id,
            'model_id': self.browse_ref('medical_clinical_laboratory.'
                                        'model_medical_laboratory_request').id,
            'type_id': self.type.id,
        })
        self.lab_activity.activate()
        self.env['workflow.plan.definition.action'].create({
            'activity_definition_id': self.activity.id,
            'direct_plan_definition_id': self.plan_definition2.id,
            'is_billable': False,
            'name': 'Action',
        })
        self.action = self.env['workflow.plan.definition.action'].create({
            'activity_definition_id': self.activity.id,
            'direct_plan_definition_id': self.plan_definition.id,
            'is_billable': True,
            'name': 'Action',
        })
        self.action2 = self.env['workflow.plan.definition.action'].create({
            'activity_definition_id': self.activity2.id,
            'direct_plan_definition_id': self.plan_definition.id,
            'is_billable': True,
            'name': 'Action2',
        })
        self.action3 = self.env['workflow.plan.definition.action'].create({
            'activity_definition_id': self.activity3.id,
            'direct_plan_definition_id': self.plan_definition.id,
            'is_billable': False,
            'name': 'Action3',
        })
        self.action4 = self.env['workflow.plan.definition.action'].create({
            'activity_definition_id': self.activity4.id,
            'direct_plan_definition_id': self.plan_definition.id,
            'is_billable': False,
            'name': 'Action4',
        })
        self.agreement_line = self.env[
            'medical.coverage.agreement.item'
        ].create({
            'product_id': self.product_01.id,
            'coverage_agreement_id': self.agreement.id,
            'plan_definition_id': self.plan_definition.id,
            'total_price': 100,
            'coverage_percentage': 50,
            'authorization_method_id': self.browse_ref(
                'cb_medical_financial_coverage_request.without').id,
            'authorization_format_id': self.browse_ref(
                'cb_medical_financial_coverage_request.format_anything').id,
        })
        self.method = self.browse_ref(
            'cb_medical_financial_coverage_request.only_number'
        )
        self.format = self.env['medical.authorization.format'].create({
            'name': 'Number',
            'code': 'testing_number',
            'always_authorized': False,
            'authorization_format': '^[0-9]*$'
        })
        self.format_letter = self.env['medical.authorization.format'].create({
            'name': 'Number',
            'code': 'testing_number',
            'always_authorized': False,
            'authorization_format': '^[a-zA-Z]*$'
        })
        self.agreement_line2 = self.env[
            'medical.coverage.agreement.item'
        ].create({
            'product_id': self.service.id,
            'coverage_agreement_id': self.agreement.id,
            'total_price': 0.0,
            'coverage_percentage': 100.0,
            'authorization_method_id': self.browse_ref(
                'cb_medical_financial_coverage_request.without').id,
            'authorization_format_id': self.browse_ref(
                'cb_medical_financial_coverage_request.format_anything').id,
        })
        self.agreement_line3 = self.env[
            'medical.coverage.agreement.item'
        ].create({
            'product_id': self.product_04.id,
            'coverage_agreement_id': self.agreement.id,
            'plan_definition_id': self.plan_definition2.id,
            'total_price': 100.0,
            'coverage_percentage': 0.0,
            'authorization_method_id': self.browse_ref(
                'cb_medical_financial_coverage_request.without').id,
            'authorization_format_id': self.browse_ref(
                'cb_medical_financial_coverage_request.format_anything').id,
        })
        self.lab_agreement_line = self.env[
            'medical.coverage.agreement.item'
        ].create({
            'product_id': self.lab_product.id,
            'coverage_agreement_id': self.agreement.id,
            'total_price': 0.0,
            'coverage_percentage': 0.0,
            'authorization_method_id': self.browse_ref(
                'cb_medical_financial_coverage_request.without').id,
            'authorization_format_id': self.browse_ref(
                'cb_medical_financial_coverage_request.format_anything').id,
        })
        self.practitioner_01 = self.create_practitioner('Practitioner 01')
        self.practitioner_02 = self.create_practitioner('Practitioner 02')
        self.product_01.medical_commission = True
        self.action.fixed_fee = 1

        self.sb_account = self.env['account.account'].create({
            'name': 'Safe box account',
            'code': '5720SBC',
            'company_id': self.company.id,
            'currency_id': self.company.currency_id.id,
            'user_type_id': self.browse_ref(
                'account.data_account_type_liquidity').id
        })
        self.bank_account = self.env['account.account'].create({
            'name': 'Bank account',
            'code': '5720BNK',
            'company_id': self.company.id,
            'currency_id': self.company.currency_id.id,
            'user_type_id': self.browse_ref(
                'account.data_account_type_liquidity').id
        })
        self.cash_account = self.env['account.account'].create({
            'name': 'Safe box account',
            'code': '572CSH',
            'company_id': self.company.id,
            'currency_id': self.company.currency_id.id,
            'user_type_id': self.browse_ref(
                'account.data_account_type_liquidity').id
        })
        self.safe_box_group = self.env['safe.box.group'].create({
            'code': 'CB',
            'name': 'CB',
            'currency_id': self.company.currency_id.id,
            'account_ids': [(6, 0, self.sb_account.ids)]
        })
        self.reina = self.env['res.partner'].create({
            'name': 'Reina',
            'is_medical': True,
            'is_center': True,
            'encounter_sequence_prefix': '9',
        })
        self.journal_1 = self.env['account.journal'].create({
            'company_id': self.company.id,
            'name': 'Bank 01',
            'type': 'bank',
            'code': 'BK01',
            'journal_user': True,
            'default_debit_account_id': self.bank_account.id,
            'default_credit_account_id': self.bank_account.id,
        })
        self.journal_1 |= self.env['account.journal'].create({
            'company_id': self.company.id,
            'name': 'Cash 01',
            'type': 'cash',
            'code': 'CASH01',
            'journal_user': True,
            'default_debit_account_id': self.cash_account.id,
            'default_credit_account_id': self.cash_account.id,
        })
        pos_vals = self.env['pos.config'].with_context(
            company_id=self.company.id
        ).default_get(
            ['journal_id', 'stock_location_id',
             'invoice_journal_id', 'pricelist_id'])
        pos_vals.update({
            'name': 'Config',
            'requires_approval': True,
            'company_id': self.company.id,
            'safe_box_group_id': self.safe_box_group.id,
            'crm_team_id': False,
            'journal_ids': [(6, 0, self.journal_1.ids)],
        })
        self.pos_config = self.env['pos.config'].create(pos_vals)
        self.pos_config.write({'session_sequence_prefix': 'POS'})
        self.assertTrue(self.pos_config.session_sequence_id)
        self.assertEqual(self.pos_config.session_sequence_id.prefix, 'POS')
        self.pos_config.write({'session_sequence_prefix': 'PS'})
        self.assertTrue(self.pos_config.session_sequence_id)
        self.assertEqual(self.pos_config.session_sequence_id.prefix, 'PS')
        self.pos_config.open_session_cb()
        self.session = self.pos_config.current_session_id
        self.session.action_pos_session_open()
        param_obj = self.env['ir.config_parameter'].sudo()
        param = param_obj.get_param('sale.default_deposit_product_id', False)
        if not param:
            param_obj.set_param(
                'sale.default_deposit_product_id',
                self.create_product('Down payment').id
            )
        self.discount = self.env['medical.sale.discount'].create({
            'name': 'Discount 01',
            'percentage': 50,
        })
        self.product = self.env['product.product'].create({
            'name': 'Product',
            'type': 'consu',
            # We don't want to check if there is enough material
            'categ_id': self.category.id,
        })
        self.reason = self.env['medical.cancel.reason'].create({
            'name': 'Cancel reason',
            'description': 'Cancel reason'
        })

    def create_patient(self, name):
        return self.env['medical.patient'].create({
            'name': name
        })

    def create_product(self, name):
        return self.env['product.product'].create({
            'type': 'service',
            'name': name,
            'taxes_id': [(6, 0, self.tax.ids)]
        })

    def create_careplan_and_group(self, agreement_line):
        encounter = self.env['medical.encounter'].create({
            'patient_id': self.patient_01.id,
            'center_id': self.center.id,
        })
        careplan_wizard = self.env[
            'medical.encounter.add.careplan'
        ].with_context(default_encounter_id=encounter.id).new({
            'coverage_id': self.coverage_01.id
        })
        careplan_wizard.onchange_coverage()
        careplan_wizard.onchange_coverage_template()
        careplan_wizard.onchange_payor()
        careplan_wizard = careplan_wizard.create(
            careplan_wizard._convert_to_write(careplan_wizard._cache))
        self.assertEqual(encounter, careplan_wizard.encounter_id)
        self.assertEqual(encounter.center_id, careplan_wizard.center_id)
        careplan_wizard.run()
        careplan = encounter.careplan_ids
        self.assertEqual(careplan.center_id, encounter.center_id)
        wizard = self.env['medical.careplan.add.plan.definition'].create({
            'careplan_id': careplan.id,
            'agreement_line_id': agreement_line.id,
        })
        self.assertIn(self.agreement, wizard.agreement_ids)
        self.action.is_billable = False
        wizard.run()
        group = self.env['medical.request.group'].search([
            ('careplan_id', '=', careplan.id)])
        group.ensure_one()
        self.assertEqual(group.center_id, encounter.center_id)
        return encounter, careplan, group

    def create_practitioner(self, name):
        return self.env['res.partner'].create({
            'name': name,
            'is_practitioner': True,
            'agent': True,
            'commission': self.browse_ref(
                'cb_medical_commission.commission_01').id,
        })

    def test_laboratory(self):
        self.plan_definition.is_billable = True
        self.plan_definition.is_breakdown = False
        self.action4 = self.env['workflow.plan.definition.action'].create({
            'activity_definition_id': self.lab_activity.id,
            'direct_plan_definition_id': self.plan_definition.id,
            'is_billable': False,
            'name': 'Action4',
        })
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line
        )
        self.assertTrue(group.laboratory_request_ids)
        action = group.with_context(
            model_name='medical.laboratory.request'
        ).action_view_request()
        self.assertEqual(
            group.laboratory_request_ids,
            self.env['medical.laboratory.request'].search(action['domain']))
        with self.assertRaises(ValidationError):
            self.env['wizard.medical.encounter.close'].create({
                'encounter_id': encounter.id,
                'pos_session_id': self.session.id,
            }).run()
        for lab_req in group.laboratory_request_ids:
            self.assertEqual(lab_req.laboratory_event_count, 0)
            event = lab_req.generate_event({
                'is_sellable_insurance': True,
                'is_sellable_private': True,
                'private_amount': 20,
                'commission_agent_id': self.practitioner_01.id,
                'coverage_amount': 10,
                'private_cost': 18,
                'coverage_cost': 9,
            })
            self.assertEqual(
                event.id, lab_req.action_view_laboratory_events()['res_id'])
            self.assertEqual(lab_req.laboratory_event_count, 1)
            lab_req.generate_event({
                'is_sellable_insurance': False,
                'is_sellable_private': False,
                'private_amount': 20,
                'commission_agent_id': self.practitioner_01.id,
                'coverage_amount': 10,
                'private_cost': 18,
                'coverage_cost': 9,
            })
            self.assertEqual(lab_req.laboratory_event_count, 2)
        self.env['wizard.medical.encounter.close'].create({
            'encounter_id': encounter.id,
            'pos_session_id': self.session.id,
        }).run()
        self.assertIn(encounter.state, ['finished', 'onleave'])
        self.assertTrue(
            encounter.sale_order_ids.mapped('order_line').filtered(
                lambda r: r.laboratory_event_id
            )
        )
        self.assertGreater(
            sum(a.amount for a in encounter.sale_order_ids.mapped(
                'order_line').filtered(
                    lambda r: r.laboratory_event_id
                ).mapped('agents')), 0)

    def test_trigger(self):
        self.plan_definition.is_billable = True
        self.plan_definition.is_breakdown = False
        self.action2.write({
            'trigger_action_ids': [(4, self.action.id)]
        })
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line
        )
        self.assertTrue(group.procedure_request_ids.filtered(
            lambda r: r.trigger_ids
        ))
        self.assertTrue(group.medication_request_ids.filtered(
            lambda r: r.triggerer_ids
        ))

    def test_cancel_encounter(self):
        self.plan_definition.is_breakdown = True
        self.plan_definition.is_billable = True
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line3
        )
        self.env['medical.encounter.cancel'].create({
            'encounter_id': encounter.id,
            'cancel_reason_id': self.reason.id,
            'cancel_reason': 'testing purposes',
            'pos_session_id': self.session.id,
        }).run()
        careplan.refresh()
        self.assertEqual(careplan.state, 'cancelled')
        self.assertIn(encounter.state, ['onleave', 'finished'])

    def test_cancel_encounter_failure(self):
        self.plan_definition.is_breakdown = True
        self.plan_definition.is_billable = True
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line3
        )
        careplan.draft2active()
        careplan.active2completed()
        with self.assertRaises(ValidationError):
            self.env['medical.encounter.cancel'].create({
                'encounter_id': encounter.id,
                'cancel_reason_id': self.reason.id,
                'cancel_reason': 'testing purposes',
                'pos_session_id': self.session.id,
            }).run()

    def test_discount(self):
        method = self.browse_ref(
            'cb_medical_sale_invoice_group_method.no_invoice')
        self.plan_definition2.third_party_bill = False
        self.plan_definition.is_breakdown = True
        self.plan_definition.is_billable = True
        self.agreement.invoice_group_method_id = method
        self.agreement_line3.coverage_percentage = 100
        self.company.sale_merge_draft_invoice = True
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line3
        )
        self.assertFalse(group.medical_sale_discount_id)
        discount = self.env['medical.request.group.discount'].new({
            'request_group_id': group.id
        })
        discount.medical_sale_discount_id = self.discount
        discount._onchange_discount()
        discount.run()
        self.assertEqual(discount.discount, self.discount.percentage)
        self.env['wizard.medical.encounter.close'].create({
            'encounter_id': encounter.id,
            'pos_session_id': self.session.id,
        }).run()
        self.assertTrue(encounter.sale_order_ids)
        sale_order = encounter.sale_order_ids
        self.assertEqual(sale_order.amount_total, 50)
        self.assertEqual(sale_order.order_line.discount, 50)

    def test_careplan_sale_fail(self):
        encounter = self.env['medical.encounter'].create({
            'patient_id': self.patient_01.id,
            'center_id': self.center.id,
        })
        careplan = self.env['medical.careplan'].new({
            'patient_id': self.patient_01.id,
            'encounter_id': encounter.id,
            'coverage_id': self.coverage_01.id,
            'sub_payor_id': self.sub_payor.id,
        })
        careplan._onchange_encounter()
        careplan = careplan.create(careplan._convert_to_write(careplan._cache))
        self.assertEqual(careplan.center_id, encounter.center_id)
        self.env['wizard.medical.encounter.add.amount'].create({
            'encounter_id': encounter.id,
            'amount': 10,
            'pos_session_id': self.session.id,
            'journal_id': self.session.journal_ids[0].id,
        }).run()
        wizard = self.env['medical.careplan.add.plan.definition'].create({
            'careplan_id': careplan.id,
            'agreement_line_id': self.agreement_line.id,
        })
        with self.assertRaises(ValidationError):
            wizard.run()

    def test_careplan_sale(self):
        encounter = self.env['medical.encounter'].create({
            'patient_id': self.patient_01.id,
            'center_id': self.center.id,
        })
        encounter_02 = self.env['medical.encounter'].create({
            'patient_id': self.patient_01.id,
            'center_id': self.center.id,
        })
        careplan = self.env['medical.careplan'].new({
            'patient_id': self.patient_01.id,
            'encounter_id': encounter.id,
            'coverage_id': self.coverage_01.id,
            'sub_payor_id': self.sub_payor.id,
        })
        careplan._onchange_encounter()
        careplan = careplan.create(careplan._convert_to_write(careplan._cache))
        self.assertEqual(careplan.center_id, encounter.center_id)
        invoice = self.env['wizard.medical.encounter.add.amount'].create({
            'encounter_id': encounter.id,
            'amount': 10,
            'pos_session_id': self.session.id,
            'journal_id': self.session.journal_ids[0].id,
        })._run()
        for line in invoice.invoice_line_ids:
            self.assertNotEqual(line.name, '/')
        wizard = self.env['medical.careplan.add.plan.definition'].create({
            'careplan_id': careplan.id,
            'agreement_line_id': self.agreement_line.id,
        })
        self.action.is_billable = False
        wizard.run()
        self.assertTrue(self.session.action_view_sale_orders()['res_id'])
        groups = self.env['medical.request.group'].search([
            ('careplan_id', '=', careplan.id)])
        self.assertTrue(groups)
        medication_requests = self.env['medical.medication.request'].search([
            ('careplan_id', '=', careplan.id)
        ])
        self.assertEqual(careplan.state, 'draft')
        self.assertTrue(medication_requests.filtered(lambda r: r.is_billable))
        self.assertTrue(medication_requests.filtered(
            lambda r: r.is_sellable_insurance or r.is_sellable_private))
        self.assertFalse(encounter.medication_item_ids)
        self.env['medical.encounter.medication'].create({
            'medical_id': encounter.id,
            'product_id': self.product_03.id,
            'location_id': self.location.id,
        }).run()
        self.assertTrue(encounter.medication_item_ids)
        self.env['medical.encounter.medication'].create({
            'medical_id': encounter.id,
            'product_id': self.product_03.id,
            'location_id': self.location.id,
        }).run()
        self.env['wizard.medical.encounter.close'].create({
            'encounter_id': encounter.id,
            'pos_session_id': self.session.id,
        }).run()
        self.assertTrue(encounter.sale_order_ids)
        self.assertTrue(encounter.has_preinvoicing)
        self.assertGreater(self.session.encounter_count, 0)
        self.assertGreater(self.session.sale_order_count, 0)
        self.assertEqual(self.session.action_view_encounters()['res_id'],
                         encounter.id)
        journal = self.session.statement_ids.mapped('journal_id')[0]
        self.assertTrue(journal)
        self.assertGreater(encounter.pending_private_amount, 0)
        lines = len(self.session.statement_ids.filtered(
            lambda r: r.journal_id == journal).mapped('line_ids'))
        self.env['wizard.medical.encounter.finish'].create({
            'encounter_id': encounter.id,
            'pos_session_id': self.session.id,
            'journal_id': journal.id,
        }).run()
        invoice = encounter.sale_order_ids.filtered(
            lambda r: not r.coverage_agreement_id and not r.is_down_payment
        ).mapped('invoice_ids')
        for line in invoice.invoice_line_ids:
            self.assertNotEqual(line.name, '/')
        self.assertGreater(len(self.session.statement_ids.filtered(
            lambda r: r.journal_id == journal).mapped('line_ids')), lines)
        self.assertEqual(encounter.pending_private_amount, 0)
        self.session.action_pos_session_closing_control()
        self.assertTrue(self.session.invoice_ids)
        self.assertTrue(self.session.sale_order_line_ids)
        self.assertTrue(self.session.request_group_ids)
        self.assertTrue(self.session.down_payment_ids)
        self.session.action_pos_session_approve()
        self.assertEqual(self.session.validation_status, 'in_progress')
        self.assertFalse(self.session.open_validation_encounter('TEST').get(
            'res_id'))

        procedure_requests = self.env['medical.procedure.request'].search([
            ('careplan_id', '=', careplan.id)
        ])
        self.assertGreater(len(procedure_requests), 0)
        medication_requests = self.env['medical.medication.request'].search([
            ('careplan_id', '=', careplan.id)
        ])
        self.assertGreater(len(medication_requests), 0)
        for sale_order in encounter.sale_order_ids:
            sale_order.recompute_lines_agents()
            self.assertEqual(sale_order.commission_total, 0)
            medicaments = self.env['sale.order.line'].search([
                ('order_id', '=', sale_order.id),
                ('product_id', '=', self.service.id),
            ])
            for medicament in medicaments:
                medicament_price = medicament.price_unit
                self.assertEqual(medicament_price, 20.0)
        procedure_requests = self.env['medical.procedure.request'].search([
            ('careplan_id', '=', careplan.id)
        ])
        self.assertGreater(len(procedure_requests), 0)
        for request in procedure_requests:
            self.assertEqual(request.center_id, encounter.center_id)
            self.assertEqual(request.state, 'draft')
            procedure = request.generate_event()
            self.assertEqual(request.state, 'active')
            procedure.performer_id = self.practitioner_01
            procedure.commission_agent_id = self.practitioner_01
            procedure.performer_id = self.practitioner_02
            procedure._onchange_performer_id()
            self.assertEqual(
                procedure.commission_agent_id, self.practitioner_02)
            procedure.preparation2in_progress()
            procedure.in_progress2completed()
            self.assertEqual(request.state, 'completed')
        for group in careplan.request_group_ids:
            self.assertEqual(group.state, 'completed')
        self.assertEqual(careplan.state, 'completed')
        encounter.recompute_commissions()
        self.assertTrue(encounter.sale_order_ids)
        for sale_order in encounter.sale_order_ids.filtered(
                lambda r: not r.is_down_payment
        ):
            self.assertTrue(sale_order.patient_name)
            original_patient_name = sale_order.patient_name
            patient_name = '%s %s' % (original_patient_name, 'TEST')
            sale_order.patient_name = patient_name
            for line in sale_order.order_line:
                self.assertTrue(line.tax_id)
                self.assertEqual(line.is_private,
                                 not bool(sale_order.coverage_agreement_id))
                self.assertEqual(line.patient_name, patient_name)
            line = sale_order.order_line[0]
            line.patient_name = original_patient_name
            self.assertEqual(sale_order.patient_name, original_patient_name)
            sale_order.recompute_lines_agents()
            self.assertGreater(sale_order.commission_total, 0)
        preinvoice_obj = self.env['sale.preinvoice.group']
        self.assertFalse(preinvoice_obj.search([
            ('agreement_id', '=', self.agreement.id)]))
        self.env['wizard.sale.preinvoice.group'].create({
            'company_ids': [(6, 0, self.company.ids)],
            'payor_ids': [(6, 0, self.payor.ids)]
        }).run()
        self.assertFalse(preinvoice_obj.search([
            ('agreement_id', '=', self.agreement.id)]))
        self.assertTrue(encounter.sale_order_ids)
        for sale_order in encounter.sale_order_ids:
            sale_order.action_confirm()
            self.assertIn(sale_order.state, ['done', 'sale'])
        self.assertTrue(encounter.sale_order_ids.filtered(
            lambda r:
            r.invoice_status == 'to preinvoice' and
            r.invoice_group_method_id == self.browse_ref(
                'cb_medical_sale_invoice_group_method.by_preinvoicing')
        ))
        self.env['wizard.sale.preinvoice.group'].create({
            'company_ids': [(6, 0, self.company.ids)],
            'payor_ids': [(6, 0, self.payor.ids)]
        }).run()
        preinvoices = preinvoice_obj.search([
            ('agreement_id', '=', self.agreement.id),
            ('state', '=', 'draft')
        ])
        self.assertTrue(preinvoices)
        # Test cancellation of preinvoices
        for preinvoice in preinvoices:
            self.assertFalse(preinvoice.validated_line_ids)
            preinvoice.cancel()
            self.assertFalse(preinvoice.line_ids)
        preinvoices = preinvoice_obj.search([
            ('agreement_id', '=', self.agreement.id),
            ('state', '=', 'draft')
        ])
        self.assertFalse(preinvoices)
        self.env['wizard.sale.preinvoice.group'].create({
            'company_ids': [(6, 0, self.company.ids)],
            'payor_ids': [(6, 0, self.payor.ids)]
        }).run()
        preinvoices = preinvoice_obj.search([
            ('agreement_id', '=', self.agreement.id),
            ('state', '=', 'draft')
        ])
        self.assertTrue(preinvoices)
        # Test unlink of not validated order_lines
        for preinvoice in preinvoices:
            self.assertTrue(preinvoice.non_validated_line_ids)
            self.assertFalse(preinvoice.validated_line_ids)
            preinvoice.start()
            preinvoice.close_sorting()
            self.assertTrue(preinvoice.non_validated_line_ids)
            preinvoice.close()
            self.assertFalse(preinvoice.non_validated_line_ids)
        preinvoices = preinvoice_obj.search([
            ('agreement_id', '=', self.agreement.id),
            ('state', '=', 'draft')
        ])
        self.assertFalse(preinvoices)
        self.env['wizard.sale.preinvoice.group'].create({
            'company_ids': [(6, 0, self.company.ids)],
            'payor_ids': [(6, 0, self.payor.ids)]
        }).run()
        preinvoices = preinvoice_obj.search([
            ('agreement_id', '=', self.agreement.id),
            ('state', '=', 'draft')
        ])
        self.assertTrue(preinvoices)
        invoice_obj = self.env['account.invoice']
        self.assertFalse(invoice_obj.search([
            ('partner_id', '=', self.payor.id)
        ]))
        # Test barcodes
        for preinvoice in preinvoices:
            self.assertFalse(preinvoice.validated_line_ids)
            preinvoice.start()
            barcode = self.env['wizard.sale.preinvoice.group.barcode'].create({
                'preinvoice_group_id': preinvoice.id,
            })
            barcode.on_barcode_scanned(encounter.internal_identifier)
            self.assertEqual(barcode.status_state, 0)
            barcode.on_barcode_scanned('No Barcode')
            self.assertEqual(barcode.status_state, 1)
            barcode.on_barcode_scanned(encounter_02.internal_identifier)
            self.assertEqual(barcode.status_state, 1)
            preinvoice.close_sorting()
            preinvoice.close()
            self.assertTrue(preinvoice.invoice_id)
        invoices = invoice_obj.search([
            ('partner_id', 'in', [self.payor.id, self.sub_payor.id])
        ])
        self.assertTrue(invoices)
        # Test invoice unlink
        for invoice in invoices:
            self.assertEqual(invoice.state, 'draft')
            invoice.invoice_line_ids.unlink()
        for sale_order in encounter.sale_order_ids:
            for line in sale_order.order_line:
                self.assertFalse(line.preinvoice_group_id)
        # Test manual validation of lines on preinvoices
        preinvoices = preinvoice_obj.search([
            ('agreement_id', '=', self.agreement.id),
            ('state', '=', 'draft')
        ])
        self.assertFalse(preinvoices)
        self.env['wizard.sale.preinvoice.group'].create({
            'company_ids': [(6, 0, self.company.ids)],
            'payor_ids': [(6, 0, self.payor.ids)]
        }).run()
        preinvoices = preinvoice_obj.search([
            ('agreement_id', '=', self.agreement.id),
            ('state', '=', 'draft')
        ])
        self.assertTrue(preinvoices)
        for preinvoice in preinvoices:
            self.assertFalse(preinvoice.validated_line_ids)
            preinvoice.start()
            for line in preinvoice.line_ids:
                line.validate_line()
            preinvoice.close_sorting()
            preinvoice.close()
            self.assertTrue(preinvoice.line_ids)
            self.assertTrue(preinvoice.invoice_id)
        invoices = invoice_obj.search([
            ('partner_id', 'in', [self.payor.id, self.sub_payor.id])
        ])
        self.assertTrue(invoices)
        for invoice in invoices:
            self.assertGreater(invoice.commission_total, 0)
            invoice.recompute_lines_agents()
            self.assertGreater(invoice.commission_total, 0)

    def test_no_agreement(self):
        self.plan_definition.is_breakdown = True
        self.plan_definition.is_billable = True
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line
        )
        self.assertTrue(group.is_billable)
        self.assertTrue(group.is_breakdown)
        with self.assertRaises(ValidationError):
            group.breakdown()

    def test_no_breakdown(self):
        self.plan_definition.is_billable = True
        self.plan_definition.is_breakdown = False
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line
        )
        self.assertTrue(group.is_billable)
        self.assertFalse(group.is_breakdown)
        with self.assertRaises(ValidationError):
            group.breakdown()

    def test_third_party(self):
        self.plan_definition.is_breakdown = True
        self.plan_definition.is_billable = True
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line3
        )
        self.assertEqual(encounter.sale_order_count, 0)
        self.assertTrue(group.procedure_request_ids)
        for request in group.procedure_request_ids:
            request.draft2active()
            self.assertEqual(request.center_id, encounter.center_id)
            procedure = request.generate_event()
            procedure.performer_id = self.practitioner_01
            procedure.commission_agent_id = self.practitioner_01
            procedure.performer_id = self.practitioner_02
            procedure._onchange_performer_id()
            self.assertEqual(
                procedure.commission_agent_id, self.practitioner_02)
        self.practitioner_02.third_party_sequence_id = self.env[
            'ir.sequence'].create({'name': 'sequence'})
        self.assertTrue(
            group.is_sellable_insurance or group.is_sellable_private)
        self.assertTrue(group.third_party_bill)
        self.env['wizard.medical.encounter.close'].create({
            'encounter_id': encounter.id,
            'pos_session_id': self.session.id,
        }).run()
        self.assertGreater(encounter.sale_order_count, 0)
        self.assertTrue(encounter.sale_order_ids)
        self.assertFalse(encounter.has_preinvoicing)
        sale_order = encounter.sale_order_ids
        self.assertTrue(sale_order.third_party_order)
        self.assertEqual(
            sale_order.third_party_partner_id, self.practitioner_02)
        self.assertGreater(encounter.pending_private_amount, 0)
        journal = self.session.statement_ids.mapped('journal_id')[0]
        self.env['wizard.medical.encounter.finish'].create({
            'encounter_id': encounter.id,
            'pos_session_id': self.session.id,
            'journal_id': journal.id,
        }).run()
        self.assertFalse(sale_order.invoice_ids)
        self.assertEqual(encounter.pending_private_amount, 0)
        self.session.action_pos_session_approve()

    @patch('odoo.addons.base_report_to_printer.models.printing_printer.'
           'PrintingPrinter.print_file')
    def test_document(self, mock):
        self.plan_definition.is_breakdown = True
        self.plan_definition.is_billable = True
        self.patient_01.lang = self.lang_en.code
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line)
        self.assertEqual(
            encounter.id,
            self.env['medical.encounter'].find_encounter_by_barcode(
                encounter.internal_identifier)['res_id'])
        identifier = encounter.internal_identifier
        self.assertFalse(
            self.env['medical.encounter'].find_encounter_by_barcode(
                '%s-%s-%s' % (identifier, identifier, identifier)
            ).get('res_id', False))
        self.assertTrue(careplan.document_reference_ids)
        self.assertTrue(group.document_reference_ids)
        documents = group.document_reference_ids.filtered(
            lambda r: r.document_type == 'action'
        )
        self.assertTrue(documents)
        for document in documents:
            self.assertEqual(
                encounter.id,
                self.env['medical.encounter'].find_encounter_by_barcode(
                    document.internal_identifier)['res_id'])
            with self.assertRaises(ValidationError):
                document.current2superseded()
            self.assertEqual(document.state, 'draft')
            self.assertTrue(document.is_editable)
            self.assertFalse(document.text)
            document.view()
            with self.assertRaises(ValidationError):
                document.draft2current()
            self.assertEqual(document.state, 'current')
            self.assertFalse(document.is_editable)
            self.assertTrue(document.text)
            self.assertEqual(
                document.text,
                '<p>%s</p><p>%s</p>' % (
                    self.patient_01.lang, self.patient_01.name))
            self.patient_01.name = self.patient_01.name + ' Other name'
            document.view()
            self.assertEqual(document.state, 'current')
            self.assertEqual(document.lang, self.patient_01.lang)
            self.assertNotEqual(
                document.text,
                '<p>%s</p><p>%s</p>' % (
                    self.patient_01.lang, self.patient_01.name))
            language_change = self.env[
                'medical.document.reference.change.language'
            ].new({
                'document_reference_id': document.id,
            })
            self.assertEqual(language_change.lang_ids, self.lang_es)
            self.env[
                'medical.document.reference.change.language'
            ].new({
                'document_reference_id': document.id,
                'lang_id': self.lang_es.id
            }).run()
            self.assertEqual(document.lang, self.lang_es.code)
            self.assertEqual(
                document.text,
                '<p>%s</p><p>%s</p>' % (
                    self.lang_es.code, self.patient_01.name))
            document.current2superseded()
            self.assertEqual(document.state, 'superseded')
            self.assertIsInstance(document.render(), bytes)
            with self.assertRaises(ValidationError):
                document.current2superseded()
            with patch('odoo.addons.base_remote.models.base.Base.remote',
                       new=self.remote):
                document.print()
                # We must verify that the document print cannot be changed
        documents = group.document_reference_ids.filtered(
            lambda r: r.document_type == 'zpl2'
        )
        self.assertTrue(documents)
        for document in documents:
            self.assertEqual(
                document.render(),
                base64.b64encode((
                    # Label start
                    '^XA\n'
                    # Print width
                    '^PW480\n'
                    # UTF-8 encoding
                    '^CI28\n'
                    # Label position
                    '^LH10,10\n'
                    # Pased encounter
                    '^FO10,10^A0N,10,10^FD%s^FS\n'
                    # Recall last saved parameters
                    '^JUR\n'
                    # Label end
                    '^XZ' % encounter.internal_identifier).encode('utf-8')))
            with self.assertRaises(UserError):
                document.view()
            with patch('odoo.addons.base_remote.models.base.Base.remote',
                       new=self.remote):
                document.print()
        self.assertTrue(group.is_billable)
        self.assertTrue(group.is_breakdown)
        self.env[
            'medical.coverage.agreement.item'
        ].create({
            'product_id': self.product_02.id,
            'coverage_agreement_id': self.agreement.id,
            'total_price': 110,
            'coverage_percentage': 0.5,
            'authorization_method_id': self.browse_ref(
                'cb_medical_financial_coverage_request.without').id,
            'authorization_format_id': self.browse_ref(
                'cb_medical_financial_coverage_request.format_anything').id,
        })
        group.breakdown()
        self.assertFalse(group.is_billable)
        self.assertFalse(group.is_breakdown)
        self.env['wizard.medical.encounter.close'].create({
            'encounter_id': encounter.id,
            'pos_session_id': self.session.id,
        }).run()
        self.assertGreater(len(encounter.sale_order_ids), 0)

    def test_validation(self):
        method = self.browse_ref(
            'cb_medical_sale_invoice_group_method.by_preinvoicing')
        self.plan_definition2.third_party_bill = False
        self.plan_definition.is_breakdown = True
        self.plan_definition.is_billable = True
        self.agreement.invoice_group_method_id = method
        self.agreement_line3.coverage_percentage = 100
        self.company.sale_merge_draft_invoice = True
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line3
        )
        self.assertTrue(group.procedure_request_ids)
        self.assertTrue(
            group.is_sellable_insurance or group.is_sellable_private)
        self.assertFalse(
            group.third_party_bill
        )
        self.env['wizard.medical.encounter.close'].create({
            'encounter_id': encounter.id,
            'pos_session_id': self.session.id,
        }).run()
        self.assertTrue(encounter.sale_order_ids)
        self.session.action_pos_session_close()
        self.pos_config.write({'session_sequence_prefix': 'POS'})
        self.assertTrue(self.pos_config.session_sequence_id)
        self.assertEqual(self.pos_config.session_sequence_id.prefix, 'POS')
        self.pos_config.write({'session_sequence_prefix': 'PS'})
        self.assertTrue(self.pos_config.session_sequence_id)
        self.assertEqual(self.pos_config.session_sequence_id.prefix, 'PS')
        self.pos_config.open_session_cb()
        self.assertTrue(self.session.request_group_ids)
        self.assertFalse(encounter.is_preinvoiced)
        line = encounter.sale_order_ids.order_line
        with self.assertRaises(ValidationError):
            encounter.admin_validate()
        encounter.toggle_is_preinvoiced()
        self.assertTrue(encounter.is_preinvoiced)
        self.coverage_template.write({
            'subscriber_required': True,
            'subscriber_format': '^1.*$'
        })
        with self.assertRaises(ValidationError):
            encounter.admin_validate()
        line.write({'subscriber_id': '23'})
        with self.assertRaises(ValidationError):
            encounter.admin_validate()
        line.write({
            'subscriber_id': '123',
        })
        self.agreement_line3.write({
            'authorization_format_id': self.format.id,
            'authorization_method_id': self.method.id,
        })
        action = self.env[
            'medical.request.group.check.authorization'
        ].with_context(
            line.check_authorization_action()['context']
        ).create({'authorization_number': '1234A'})
        action.run()
        self.assertNotEqual(line.authorization_status, 'authorized')
        self.assertEqual(line.authorization_number, '1234A')
        with self.assertRaises(ValidationError):
            encounter.admin_validate()
        action = self.env[
            'medical.request.group.check.authorization'
        ].with_context(
            line.check_authorization_action()['context']
        ).create({'authorization_number': '1234'})
        action.run()
        self.assertEqual(line.authorization_status, 'authorized')
        self.assertEqual(line.authorization_number, '1234')
        self.agreement_line3.write({
            'authorization_format_id': self.format_letter.id,
        })
        with self.assertRaises(ValidationError):
            encounter.admin_validate()
        self.agreement_line3.write({
            'authorization_format_id': self.format.id,
        })
        encounter.admin_validate()

    def test_patient_invoice(self):
        method = self.browse_ref(
            'cb_medical_sale_invoice_group_method.by_patient')
        self.plan_definition2.third_party_bill = False
        self.plan_definition.is_breakdown = True
        self.plan_definition.is_billable = True
        self.agreement.invoice_group_method_id = method
        self.agreement_line3.coverage_percentage = 100
        self.company.sale_merge_draft_invoice = True
        for i in range(1, 10):
            encounter, careplan, group = self.create_careplan_and_group(
                self.agreement_line3
            )
            self.assertTrue(group.procedure_request_ids)
            self.assertTrue(
                group.is_sellable_insurance or group.is_sellable_private)
            self.assertFalse(
                group.third_party_bill
            )
            self.env['wizard.medical.encounter.close'].create({
                'encounter_id': encounter.id,
                'pos_session_id': self.session.id,
            }).run()
            self.assertTrue(encounter.sale_order_ids)
            sale_order = encounter.sale_order_ids
            self.assertFalse(sale_order.third_party_order)
            for line in sale_order.order_line:
                self.assertFalse(line.agents)
        self.session.action_pos_session_close()
        self.assertTrue(self.session.request_group_ids)
        for encounter in self.session.encounter_ids:
            encounter_aux = self.env['medical.encounter'].browse(
                self.session.open_validation_encounter(
                    encounter.internal_identifier)['res_id'])
            encounter_aux.admin_validate()
            for sale_order in encounter_aux.sale_order_ids:
                self.assertTrue(sale_order.invoice_ids)
                self.assertTrue(all(
                    i.state == 'open' for i in sale_order.invoice_ids))

    def test_no_invoice(self):
        method = self.browse_ref(
            'cb_medical_sale_invoice_group_method.no_invoice')
        self.plan_definition2.third_party_bill = False
        self.plan_definition.is_breakdown = True
        self.plan_definition.is_billable = True
        self.agreement.invoice_group_method_id = method
        self.agreement_line3.coverage_percentage = 100
        self.company.sale_merge_draft_invoice = True
        sale_orders = self.env['sale.order']
        for i in range(1, 10):
            encounter, careplan, group = self.create_careplan_and_group(
                self.agreement_line3
            )
            self.assertTrue(group.procedure_request_ids)
            self.assertTrue(
                group.is_sellable_insurance or group.is_sellable_private)
            self.assertFalse(
                group.third_party_bill
            )
            self.env['wizard.medical.encounter.close'].create({
                'encounter_id': encounter.id,
                'pos_session_id': self.session.id,
            }).run()
            self.assertTrue(encounter.sale_order_ids)
            sale_order = encounter.sale_order_ids
            self.assertFalse(sale_order.third_party_order)
            for line in sale_order.order_line:
                self.assertFalse(line.agents)
            sale_orders |= sale_order
        self.session.action_pos_session_close()
        self.assertTrue(self.session.request_group_ids)
        for encounter in self.session.encounter_ids:
            encounter_aux = self.env['medical.encounter'].browse(
                self.session.open_validation_encounter(
                    encounter.internal_identifier)['res_id'])
            encounter_aux.admin_validate()
        for line in sale_orders.mapped('order_line'):
            self.assertEqual(line.qty_to_invoice, 0)
        for encounter in self.session.encounter_ids:
            for request in encounter.careplan_ids.mapped(
                    'procedure_request_ids'
            ):
                request.draft2active()
                self.assertEqual(request.center_id, encounter.center_id)
                procedure = request.generate_event()
                procedure.performer_id = self.practitioner_01
                procedure.commission_agent_id = self.practitioner_01
                procedure.performer_id = self.practitioner_02
                procedure._onchange_performer_id()
                self.assertEqual(
                    procedure.commission_agent_id, self.practitioner_02)
            encounter.recompute_commissions()
            for line in encounter.sale_order_ids.mapped('order_line'):
                self.assertTrue(line.agents)
        # Settle the payments
        wizard = self.env['sale.commission.no.invoice.make.settle'].create({
            'date_to': (
                fields.Datetime.from_string(fields.Datetime.now()) +
                relativedelta(months=1))
        })
        settlements = self.env['sale.commission.settlement'].browse(
            wizard.action_settle()['domain'][0][2])
        self.assertTrue(settlements)
        for encounter in self.session.encounter_ids:
            for request in encounter.careplan_ids.mapped(
                    'procedure_request_ids'
            ):
                procedure = request.procedure_ids
                self.assertEqual(len(procedure.sale_agent_ids), 1)
                self.assertEqual(len(procedure.invoice_agent_ids), 0)
                procedure.performer_id = self.practitioner_01
                procedure.commission_agent_id = self.practitioner_01
                procedure.check_commission()
                self.assertEqual(len(procedure.sale_agent_ids), 3)
                self.assertEqual(len(procedure.invoice_agent_ids), 0)

    def test_monthly_invoice(self):
        method = self.browse_ref(
            'cb_medical_sale_invoice_group_method.by_customer')
        self.plan_definition2.third_party_bill = False
        self.plan_definition.is_breakdown = True
        self.plan_definition.is_billable = True
        self.agreement.invoice_group_method_id = method
        self.agreement_line3.coverage_percentage = 100
        nomenclature_product = self.env['product.nomenclature.product'].create(
            {
                'nomenclature_id': self.nomenclature.id,
                'product_id':
                    self.agreement_line3.product_id.id,
                'name': 'nomenclature_name',
                'code': 'nomenclature_code',
            })
        self.company.sale_merge_draft_invoice = True
        sale_orders = self.env['sale.order']
        for i in range(1, 10):
            encounter, careplan, group = self.create_careplan_and_group(
                self.agreement_line3
            )
            self.assertTrue(group.procedure_request_ids)
            self.assertTrue(
                group.is_sellable_insurance or group.is_sellable_private)
            self.assertFalse(
                group.third_party_bill
            )
            self.env['wizard.medical.encounter.close'].create({
                'encounter_id': encounter.id,
                'pos_session_id': self.session.id,
            }).run()
            self.assertTrue(encounter.sale_order_ids)
            sale_order = encounter.sale_order_ids
            self.assertFalse(sale_order.third_party_order)
            for line in sale_order.order_line:
                self.assertFalse(line.agents)
            sale_orders |= sale_order
        self.session.action_pos_session_close()
        self.assertTrue(self.session.request_group_ids)
        for encounter in self.session.encounter_ids:
            encounter_aux = self.env['medical.encounter'].browse(
                self.session.open_validation_encounter(
                    encounter.internal_identifier)['res_id'])
            encounter_aux.admin_validate()
        action = self.env['invoice.sales.by.group'].create({
            'invoice_group_method_id': method.id,
        }).invoice_sales_by_group()
        self.assertFalse(action.get('res_id', False))
        action = self.env['invoice.sales.by.group'].create({
            'invoice_group_method_id': method.id,
            'date_to': fields.Date.to_string(
                fields.Date.from_string(fields.Date.today()) +
                timedelta(days=1)
            )
        }).invoice_sales_by_group()
        self.assertTrue(action.get('res_id', False))
        invoice = self.env['account.invoice'].browse(
            action.get('res_id', False))
        invoice.action_invoice_open()
        for line in invoice.invoice_line_ids:
            self.assertEqual(line.name, nomenclature_product.name)
        for sale_order in sale_orders:
            self.assertTrue(sale_order.invoice_status == 'invoiced')
        for encounter in self.session.encounter_ids:
            for request in encounter.careplan_ids.mapped(
                'procedure_request_ids'
            ):
                request.draft2active()
                self.assertEqual(request.center_id, encounter.center_id)
                procedure = request.generate_event()
                procedure.performer_id = self.practitioner_01
                procedure.commission_agent_id = self.practitioner_01
                procedure.performer_id = self.practitioner_02
                procedure._onchange_performer_id()
                self.assertEqual(
                    procedure.commission_agent_id, self.practitioner_02)
            encounter.recompute_commissions()
            for line in encounter.sale_order_ids.mapped('order_line'):
                self.assertTrue(line.agents)
        # Settle the payments
        wizard = self.env['sale.commission.make.settle'].create({
            'date_to': (
                fields.Datetime.from_string(fields.Datetime.now()) +
                relativedelta(months=1))
        })
        settlements = self.env['sale.commission.settlement'].browse(
            wizard.action_settle()['domain'][0][2])
        self.assertTrue(settlements)
        for encounter in self.session.encounter_ids:
            for request in encounter.careplan_ids.mapped(
                'procedure_request_ids'
            ):
                procedure = request.procedure_ids
                self.assertEqual(len(procedure.sale_agent_ids), 1)
                self.assertEqual(len(procedure.invoice_agent_ids), 1)
                procedure.performer_id = self.practitioner_01
                procedure.commission_agent_id = self.practitioner_01
                procedure.check_commission()
                self.assertEqual(len(procedure.sale_agent_ids), 1)
                self.assertEqual(len(procedure.invoice_agent_ids), 3)

    def test_down_payments(self):
        self.plan_definition2.third_party_bill = False
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line3
        )
        invoice = self.env['wizard.medical.encounter.add.amount'].create({
            'encounter_id': encounter.id,
            'pos_session_id': self.session.id,
            'journal_id': self.journal_1[0].id,
            'amount': 200
        })._run()
        self.assertEqual(invoice.type, 'out_invoice')
        invoice = self.env['wizard.medical.encounter.add.amount'].create({
            'encounter_id': encounter.id,
            'pos_session_id': self.session.id,
            'journal_id': self.journal_1[0].id,
            'amount': -100
        })._run()
        self.assertEqual(invoice.type, 'out_refund')
        self.env['wizard.medical.encounter.close'].create({
            'encounter_id': encounter.id,
            'pos_session_id': self.session.id,
        }).run()
        self.assertEqual(encounter.pending_private_amount, 0)
        self.env['wizard.medical.encounter.finish'].create({
            'encounter_id': encounter.id,
            'pos_session_id': self.session.id,
            'journal_id': self.journal_1[0].id,
        }).run()
        sale_order = encounter.sale_order_ids.filtered(
            lambda r: not r.is_down_payment)
        self.assertTrue(sale_order)
        self.assertEqual(sale_order.amount_total, 0)

    def test_down_payments_third_party(self):
        self.plan_definition2.third_party_bill = True
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line3
        )
        self.env['wizard.medical.encounter.add.amount'].create({
            'encounter_id': encounter.id,
            'pos_session_id': self.session.id,
            'journal_id': self.journal_1[0].id,
            'amount': 100
        }).run()
        for request in group.procedure_request_ids:
            request.draft2active()
            self.assertEqual(request.center_id, encounter.center_id)
            procedure = request.generate_event()
            procedure.performer_id = self.practitioner_01
            procedure.commission_agent_id = self.practitioner_01
            procedure.performer_id = self.practitioner_02
            procedure._onchange_performer_id()
            self.assertEqual(
                procedure.commission_agent_id, self.practitioner_02)
        self.practitioner_02.third_party_sequence_id = self.env[
            'ir.sequence'].create({'name': 'sequence'})
        self.env['wizard.medical.encounter.close'].create({
            'encounter_id': encounter.id,
            'pos_session_id': self.session.id,
        }).run()
        self.assertEqual(encounter.pending_private_amount, 0)
        self.env['wizard.medical.encounter.finish'].create({
            'encounter_id': encounter.id,
            'pos_session_id': self.session.id,
            'journal_id': self.journal_1[0].id,
        }).run()
        self.assertEqual(encounter.pending_private_amount, 0)
        sale_order = encounter.sale_order_ids.filtered(
            lambda r: not r.is_down_payment and not r.third_party_partner_id)
        self.assertTrue(sale_order)
        self.assertEqual(sale_order.amount_total, -100)
        payments = sale_order.invoice_ids.mapped('bank_statement_line_ids')
        self.assertTrue(payments)
        self.assertEqual(-100, payments.amount)
        sale_order = encounter.sale_order_ids.filtered(
            lambda r: not r.is_down_payment and r.third_party_partner_id)
        self.assertTrue(sale_order)
        payments = sale_order.mapped('bank_statement_line_ids')
        self.assertTrue(payments)
        self.assertEqual(100, payments.amount)
        self.assertEqual(sale_order.amount_total, 100)

    def test_careplan_add_wizard(self):
        encounter = self.env['medical.encounter'].create({
            'patient_id': self.patient_01.id,
            'center_id': self.center.id,
        })
        careplan_wizard = self.env[
            'medical.encounter.add.careplan'
        ].with_context(default_encounter_id=encounter.id).new({
            'coverage_id': self.coverage_01.id
        })
        careplan_wizard.onchange_coverage()
        careplan_wizard.onchange_coverage_template()
        careplan_wizard.onchange_payor()
        careplan_wizard = careplan_wizard.create(
            careplan_wizard._convert_to_write(careplan_wizard._cache))
        self.assertEqual(encounter, careplan_wizard.encounter_id)
        self.assertEqual(encounter.center_id, careplan_wizard.center_id)
        careplan_wizard.run()
        careplan = encounter.careplan_ids
        careplan_wizard_2 = self.env[
            'medical.encounter.add.careplan'
        ].with_context(default_encounter_id=encounter.id).new({
            'coverage_id': self.coverage_01.id
        })
        careplan_wizard_2.onchange_coverage()
        careplan_wizard_2.onchange_coverage_template()
        careplan_wizard_2.onchange_payor()
        careplan_wizard_2 = careplan_wizard_2.create(
            careplan_wizard_2._convert_to_write(careplan_wizard_2._cache))
        self.assertEqual(encounter, careplan_wizard_2.encounter_id)
        self.assertEqual(encounter.center_id, careplan_wizard_2.center_id)
        cp_2 = careplan_wizard_2.run()
        self.assertEqual(cp_2, careplan)
        careplan_wizard_3 = self.env[
            'medical.encounter.add.careplan'
        ].with_context(default_encounter_id=encounter.id).new({
            'coverage_id': self.coverage_02.id
        })
        careplan_wizard_3.onchange_coverage()
        careplan_wizard_3.onchange_coverage_template()
        careplan_wizard_3.onchange_payor()
        careplan_wizard_3 = careplan_wizard_2.create(
            careplan_wizard_3._convert_to_write(careplan_wizard_3._cache))
        self.assertEqual(encounter, careplan_wizard_3.encounter_id)
        self.assertEqual(encounter.center_id, careplan_wizard_3.center_id)
        cp_3 = careplan_wizard_3.run()
        self.assertNotEqual(cp_3, careplan)

    def test_performer(self):
        self.plan_definition2.write({
            'third_party_bill': True,
            'performer_required': True,
        })
        self.env['workflow.plan.definition.action'].create({
            'activity_definition_id': self.activity5.id,
            'direct_plan_definition_id': self.plan_definition2.id,
            'is_billable': False,
            'name': 'Action',
        })
        self.activity5.performer_id = self.practitioner_02
        encounter = self.env['medical.encounter'].create({
            'patient_id': self.patient_01.id,
            'center_id': self.center.id,
        })
        careplan_wizard = self.env[
            'medical.encounter.add.careplan'
        ].with_context(default_encounter_id=encounter.id).new({
            'coverage_id': self.coverage_01.id
        })
        careplan_wizard.onchange_coverage()
        careplan_wizard.onchange_coverage_template()
        careplan_wizard.onchange_payor()
        careplan_wizard = careplan_wizard.create(
            careplan_wizard._convert_to_write(careplan_wizard._cache))
        self.assertEqual(encounter, careplan_wizard.encounter_id)
        self.assertEqual(encounter.center_id, careplan_wizard.center_id)
        careplan_wizard.run()
        careplan = encounter.careplan_ids
        self.assertEqual(careplan.center_id, encounter.center_id)
        wizard = self.env['medical.careplan.add.plan.definition'].create({
            'careplan_id': careplan.id,
            'agreement_line_id': self.agreement_line3.id,
            'performer_id': self.practitioner_01.id
        })
        self.assertIn(self.agreement, wizard.agreement_ids)
        self.action.is_billable = False
        wizard.run()
        group = self.env['medical.request.group'].search([
            ('careplan_id', '=', careplan.id)])
        group.ensure_one()
        self.assertEqual(group.center_id, encounter.center_id)
        self.assertEqual(group.performer_id, self.practitioner_01)
        self.assertGreaterEqual(len(group.procedure_request_ids.ids), 2)
        self.assertTrue(group.procedure_request_ids.filtered(
            lambda r: r.performer_id == self.practitioner_01
        ))
        self.assertTrue(group.procedure_request_ids.filtered(
            lambda r: r.performer_id == self.practitioner_02
        ))

    def test_unblocking(self):
        self.plan_definition2.write({
            'third_party_bill': False,
        })
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line3
        )
        self.assertEqual(len(group.procedure_request_ids), 1)
        self.assertFalse(group.procedure_request_ids.is_blocking)
        self.env['wizard.medical.encounter.close'].create({
            'encounter_id': encounter.id,
            'pos_session_id': self.session.id,
        }).run()
        self.assertIn(encounter.state, ['onleave', 'finished'])

    def test_blocking_failure(self):
        self.plan_definition2.action_ids.write({
            'is_blocking': True
        })
        self.plan_definition2.write({
            'third_party_bill': False,
        })
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line3
        )
        self.assertEqual(len(group.procedure_request_ids), 1)
        self.assertTrue(group.procedure_request_ids.is_blocking)
        self.assertTrue(group.procedure_request_ids.is_blocking)
        with self.assertRaises(ValidationError):
            self.env['wizard.medical.encounter.close'].create({
                'encounter_id': encounter.id,
                'pos_session_id': self.session.id,
            }).run()

    def test_blocking_ok(self):
        self.plan_definition2.action_ids.write({
            'is_blocking': True
        })
        self.plan_definition2.write({
            'third_party_bill': False,
        })
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line3
        )
        self.assertEqual(len(group.procedure_request_ids), 1)
        self.assertTrue(group.procedure_request_ids.is_blocking)
        for request in group.procedure_request_ids:
            request.draft2active()
            procedure = request.generate_event()
            self.assertEqual(request.state, 'active')
            procedure.performer_id = self.practitioner_01
            procedure.commission_agent_id = self.practitioner_01
            procedure.performer_id = self.practitioner_02
            procedure._onchange_performer_id()
            self.assertEqual(
                procedure.commission_agent_id, self.practitioner_02)
            procedure.preparation2in_progress()
            procedure.in_progress2completed()
            self.assertEqual(request.state, 'completed')
        self.env['wizard.medical.encounter.close'].create({
            'encounter_id': encounter.id,
            'pos_session_id': self.session.id,
        }).run()
        self.assertIn(encounter.state, ['onleave', 'finished'])

    def test_practitioner_conditions(self):
        self.plan_definition2.write({
            'third_party_bill': False,
        })
        self.plan_definition2.action_ids.write({
            'variable_fee': 0,
            'fixed_fee': 10,
        })
        self.assertNotEqual(
            self.plan_definition2.action_ids.activity_definition_id.service_id,
            self.agreement_line3.product_id
        )
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line3
        )
        self.env['medical.practitioner.condition'].create({
            'practitioner_id': self.practitioner_02.id,
            'variable_fee': 10,
            'fixed_fee': 0,
            'procedure_service_id': self.agreement_line3.product_id.id,
        })
        self.assertEqual(self.agreement_line3.product_id, group.service_id)
        for request in group.procedure_request_ids:
            request.draft2active()
            procedure = request.generate_event()
            self.assertEqual(request.state, 'active')
            procedure.performer_id = self.practitioner_01
            procedure.commission_agent_id = self.practitioner_01
            procedure.performer_id = self.practitioner_02
            procedure._onchange_performer_id()
            procedure._onchange_check_condition()
            self.assertEqual(
                procedure.commission_agent_id, self.practitioner_02)
            self.assertFalse(procedure.practitioner_condition_id)
            self.assertEqual(request.variable_fee, 0)
            self.assertEqual(request.fixed_fee, 10)
            general_cond = self.env['medical.practitioner.condition'].create({
                'practitioner_id': self.practitioner_02.id,
                'variable_fee': 10,
                'fixed_fee': 0,
            })
            procedure._onchange_check_condition()
            self.assertEqual(procedure.practitioner_condition_id, general_cond)
            self.assertEqual(procedure.variable_fee, 10)
            self.assertEqual(procedure.fixed_fee, 0)
            proc_cond = self.env['medical.practitioner.condition'].create({
                'practitioner_id': self.practitioner_02.id,
                'variable_fee': 0,
                'fixed_fee': 5,
                'procedure_service_id': self.product_02.id,
            })
            procedure._onchange_check_condition()
            self.assertEqual(procedure.practitioner_condition_id, proc_cond)
            self.assertEqual(procedure.variable_fee, 0)
            self.assertEqual(procedure.fixed_fee, 5)
            group_cond = self.env['medical.practitioner.condition'].create({
                'practitioner_id': self.practitioner_02.id,
                'variable_fee': 0,
                'fixed_fee': 15,
                'service_id': self.product_04.id,
            })
            procedure._onchange_check_condition()
            self.assertEqual(procedure.practitioner_condition_id, group_cond)
            self.assertEqual(procedure.variable_fee, 0)
            self.assertEqual(procedure.fixed_fee, 15)
            cond = self.env['medical.practitioner.condition'].create({
                'practitioner_id': self.practitioner_02.id,
                'variable_fee': 0,
                'fixed_fee': 0,
                'service_id': self.product_04.id,
                'procedure_service_id': self.product_02.id,
            })
            procedure._onchange_check_condition()
            self.assertEqual(procedure.practitioner_condition_id, cond)
            self.assertEqual(procedure.variable_fee, 0)
            self.assertEqual(procedure.fixed_fee, 0)
