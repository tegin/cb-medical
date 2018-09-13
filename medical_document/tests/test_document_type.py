# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError, ValidationError


class TestMedicalDocumentType(TransactionCase):
    def setUp(self):
        super().setUp()
        self.document_type = self.env['medical.document.type'].create({
            'name': 'CI',
            'report_action_id': self.browse_ref(
                'medical_document.action_report_document_report_base').id,
        })
        self.type = self.browse_ref('medical_workflow.medical_workflow')

    def add_language(self):
        self.assertFalse(self.document_type.lang_ids)
        lang = self.env['res.lang'].search([('active', '=', True)], limit=1)
        add_language = self.env['medical.document.type.add.language'].create({
            'document_type_id': self.document_type.id,
            'lang_id': lang.id,
        })
        self.assertTrue(add_language.lang_id.filtered(
            lambda r: r.code == lang.code))
        add_language.run()
        self.assertTrue(self.document_type.lang_ids)
        self.document_type.lang_ids.filtered(
            lambda r: r.lang == lang.code
        ).write({
            'text': '<p>I, ${object.patient_id.name}, recognize the protocol'
                    ' ${object.name} and sign this document.</p>'
                    '<p>Signed:${object.patient_id.name}<br></p>',
        })
        add_language = self.env['medical.document.type.add.language'].new({
            'document_type_id': self.document_type.id,
        })
        self.assertFalse(add_language.lang_id.filtered(
            lambda r: r.code == lang.code))

    def test_document_type(self):
        self.add_language()
        self.assertEqual(self.document_type.state, 'draft')
        self.document_type.draft2current()
        self.assertEqual(self.document_type.state, 'current')
        self.assertEqual(len(self.document_type.template_ids), 1)
        self.document_type.post()
        self.assertEqual(len(self.document_type.template_ids), 2)
        self.document_type.current2superseded()
        self.assertEqual(self.document_type.state, 'superseded')

    def test_failure(self):
        self.assertEqual(self.document_type.state, 'draft')
        self.document_type.draft2current()
        self.assertEqual(self.document_type.state, 'current')
        template = self.document_type.current_template_id
        with self.assertRaises(UserError):
            template.render_template(template._name, template.id)

    def test_activity_definition(self):
        self.add_language()
        self.document_type.draft2current()
        activity_def = self.env['workflow.activity.definition'].new({
            'name': 'Activity3',
            'model_id': self.browse_ref(
                'medical_document.model_medical_document_reference').id,
            'type_id': self.type.id,
            'document_type_id': self.document_type.id,
            'state': 'active'
        })
        self.assertTrue(activity_def.requires_document_template)
        activity_def.update({
            'model_id': self.browse_ref(
                'medical_document.model_medical_document_type').id,
        })
        self.assertFalse(activity_def.requires_document_template)
        activity_def._onchange_model()
        self.assertFalse(activity_def.document_type_id)

        activity_def.update({
            'model_id': self.browse_ref(
                'medical_document.model_medical_document_reference').id,
        })
        self.assertTrue(activity_def.requires_document_template)
        activity_def.document_type_id = self.document_type
        activity_def = activity_def.create(activity_def._convert_to_write(
            activity_def._cache))
        with self.assertRaises(ValidationError):
            self.document_type.current2superseded()
        activity_def.state = 'retired'
        self.document_type.current2superseded()
        self.assertEqual(self.document_type.state, 'superseded')
