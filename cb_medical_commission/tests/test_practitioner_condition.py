from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestPractitionerCondition(TransactionCase):

    def test_condition(self):
        practitioner = self.env['res.partner'].create({
            'name': 'Practitioner',
            'is_medical': True,
            'is_practitioner': True
        })
        service = self.env['product.product'].create({
            'name': 'Service',
            'type': 'service'
        })
        self.env['medical.practitioner.condition'].create({
            'practitioner_id': practitioner.id,
        })
        self.env['medical.practitioner.condition'].create({
            'practitioner_id': practitioner.id,
            'service_id': service.id,
        })
        self.env['medical.practitioner.condition'].create({
            'practitioner_id': practitioner.id,
            'procedure_service_id': service.id,
        })
        self.env['medical.practitioner.condition'].create({
            'practitioner_id': practitioner.id,
            'service_id': service.id,
            'procedure_service_id': service.id,
        })
        with self.assertRaises(ValidationError):
            self.env['medical.practitioner.condition'].create({
                'practitioner_id': practitioner.id,
                'procedure_service_id': service.id,
            })

    def test_condition_archived(self):
        practitioner = self.env['res.partner'].create({
            'name': 'Practitioner',
            'is_medical': True,
            'is_practitioner': True
        })
        service = self.env['product.product'].create({
            'name': 'Service',
            'type': 'service'
        })
        self.env['medical.practitioner.condition'].create({
            'practitioner_id': practitioner.id,
        })
        self.env['medical.practitioner.condition'].create({
            'practitioner_id': practitioner.id,
            'service_id': service.id,
        })
        condition = self.env['medical.practitioner.condition'].create({
            'practitioner_id': practitioner.id,
            'procedure_service_id': service.id,
        })
        self.env['medical.practitioner.condition'].create({
            'practitioner_id': practitioner.id,
            'service_id': service.id,
            'procedure_service_id': service.id,
        })
        condition.toggle_active()
        self.env['medical.practitioner.condition'].create({
            'practitioner_id': practitioner.id,
            'procedure_service_id': service.id,
        })
