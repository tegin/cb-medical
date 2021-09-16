# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):

    openupgrade.logged_query(
        env.cr,
        """
        UPDATE sale_order_line
        SET medical_model = 'medical.careplan',
            medical_res_id = careplan_id
        WHERE careplan_id is not null
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE sale_order_line
        SET medical_model = 'medical.procedure.request',
            medical_res_id = procedure_request_id
        WHERE procedure_request_id is not null
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE sale_order_line
        SET medical_model = 'medical.request.group',
            medical_res_id = request_group_id
        WHERE request_group_id is not null
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE sale_order_line
        SET medical_model = 'medical.medication.request',
            medical_res_id = medication_request_id
        WHERE medication_request_id is not null
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE sale_order_line
        SET medical_model = 'medical.document.reference',
            medical_res_id = document_reference_id
        WHERE document_reference_id is not null
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE sale_order_line
        SET medical_model = 'medical.laboratory.request',
            medical_res_id = laboratory_request_id
        WHERE laboratory_request_id is not null
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE sale_order_line
        SET medical_model = 'medical.laboratory.event',
            medical_res_id = laboratory_event_id
        WHERE laboratory_event_id is not null
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move am
        SET is_medical = ai.is_medical,
            show_patient = ai.show_patient,
            show_subscriber = ai.show_subscriber,
            show_authorization = ai.show_authorization,
            encounter_id = ai.encounter_id
        FROM account_invoice ai
        WHERE ai.id = am.old_invoice_id""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move_line aml
        SET patient_id = ail.patient_id,
            encounter_id = ail.encounter_id,
            patient_name = ail.patient_name,
            subscriber_id = ail.subscriber_id,
            authorization_number = ail.authorization_number
        FROM account_invoice_line ail
        WHERE ail.id = aml.old_invoice_line_id""",
    )
