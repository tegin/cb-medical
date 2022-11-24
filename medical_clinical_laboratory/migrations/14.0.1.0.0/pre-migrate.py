# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_field_renames = [
    ("medical.laboratory.request", "medical_laboratory_request", "state", "fhir_state"),
    ("medical.laboratory.event", "medical_laboratory_event", "state", "fhir_state"),
]
_field_news = [
    (
        "state",
        "medical.laboratory.request",
        "medical_laboratory_request",
        "selection",
        False,
        "medical_clinical_laboratory",
        "done",
    ),
    (
        "state",
        "medical.laboratory.event",
        "medical_laboratory_event",
        "selection",
        False,
        "medical_clinical_laboratory",
        "done",
    ),
]


@openupgrade.migrate()
def migrate(env, version):
    if not openupgrade.column_exists(env.cr, "medical_procedure_request", "fhir_state"):
        openupgrade.rename_fields(env, _field_renames)
        openupgrade.add_fields(env, _field_news)
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE medical_laboratory_request
                SET state = 'draft'
            WHERE fhir_state in ('draft', 'active')
        """,
        )
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE medical_laboratory_event
                SET state = 'draft'
            WHERE fhir_state in ('preparation', 'in-progress')
        """,
        )
