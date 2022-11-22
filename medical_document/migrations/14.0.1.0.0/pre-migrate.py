# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_field_renames = [
    ("medical.document.reference", "medical_document_reference", "state", "fhir_state"),
]
_field_news = [
    (
        "state",
        "medical.document.reference",
        "medical_document_reference",
        "selection",
        False,
        "medical_document",
        "done",
    ),
]


@openupgrade.migrate()
def migrate(env, version):
    if not openupgrade.column_exists(
        env.cr, "medical_document_reference", "fhir_state"
    ):
        openupgrade.rename_fields(env, _field_renames)
        openupgrade.add_fields(env, _field_news)
        openupgrade.logged_query(
            env.cr,
            """
                UPDATE medical_document_reference
                    SET state = 'draft'
                WHERE fhir_state in ('draft')
            """,
        )
