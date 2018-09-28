# Copyright 2017 LasLabs Inc.
# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase


class TestMedicalAdministrationHealthcareService(TransactionCase):

    def setUp(self):
        super().setUp()
        self.healthcare_service_model = self.env['res.partner']

    def test_service(self):
        healthcare_service_vals = {
            'is_medical': True,
            'is_healthcare_service': True,
            'name': 'Laboratory',
        }
        healthcare_service_1 = self.healthcare_service_model.create(
            healthcare_service_vals)
        self.assertTrue(healthcare_service_1)
        self.assertTrue(healthcare_service_1.healthcare_service_identifier)
