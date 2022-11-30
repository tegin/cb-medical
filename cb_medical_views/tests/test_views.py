import json

from odoo.addons.cb_medical_careplan_sale.tests import common


class TestCBSale(common.MedicalSavePointCase):
    def test_search_encounter_01(self):
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line3
        )
        encounter_search = self.env["medical.encounter"].find_encounter_by_barcode(
            encounter.internal_identifier
        )
        self.assertEqual(
            encounter,
            self.env[encounter_search["res_model"]].browse(encounter_search["res_id"]),
        )

    def test_search_encounter_02(self):
        encounter, careplan, group = self.create_careplan_and_group(self.agreement_line)
        documents = self.env["medical.document.reference"].search(
            [("encounter_id", "=", encounter.id)], limit=1
        )
        self.assertTrue(documents)
        for document in documents:
            encounter_search = self.env["medical.encounter"].find_encounter_by_barcode(
                document.internal_identifier
            )
            self.assertEqual(
                encounter,
                self.env[encounter_search["res_model"]].browse(
                    encounter_search["res_id"]
                ),
            )

    def test_search_encounter_fails(self):
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line3
        )
        encounter_search = self.env["medical.encounter"].find_encounter_by_barcode(
            encounter.internal_identifier + encounter.internal_identifier
        )
        self.assertEqual("barcode.action", encounter_search["res_model"])
        self.assertEqual(
            json.loads(encounter_search["context"])["default_state"], "warning"
        )

    def test_encounter_display(self):
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line3
        )
        self.assertRegex(
            encounter.display_name, "^.*%s.*$" % encounter.internal_identifier
        )

    def test_request_display(self):
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line3
        )
        self.assertRegex(
            careplan.display_name, "^.*%s.*$" % careplan.internal_identifier
        )

    def test_event_display(self):
        encounter, careplan, group = self.create_careplan_and_group(
            self.agreement_line3
        )
        requests = group.procedure_request_ids
        self.assertTrue(requests)
        request = requests[0]
        event = request.generate_event()
        self.assertRegex(event.display_name, "^.*%s.*$" % event.internal_identifier)

    def test_coverage_display(self):
        self.assertEqual(
            self.coverage_01.display_name, self.coverage_01.internal_identifier
        )
        self.coverage_01.name = "COVERAGE NAME"
        self.assertEqual(self.coverage_01.display_name, "COVERAGE NAME")
        self.coverage_01.refresh()
        self.coverage_01.subscriber_id = "1234"
        self.assertEqual(self.coverage_01.display_name, "1234")

    def test_coverage_template_display(self):
        display_name = self.coverage_template.display_name
        self.assertRegex(display_name, "^.*%s.*$" % self.payor.display_name)
        self.assertRegex(display_name, "^.*%s.*$" % self.coverage_template.display_name)
