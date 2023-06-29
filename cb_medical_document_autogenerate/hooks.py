from openupgradelib import openupgrade


def post_init_hook(cr, registry):
    openupgrade.logged_query(
        cr,
        """
        UPDATE medical_document_reference
        SET autogenerated=TRUE
    """,
    )