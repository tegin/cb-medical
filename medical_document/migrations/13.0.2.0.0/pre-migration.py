from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_columns(
        env.cr, {"medical_document_reference": [("text", "database_text")]}
    )
