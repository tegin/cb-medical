# Copyright 2024 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
    UPDATE medical_request_group mrg
    SET generate_queue_task = wpd.generate_queue_task,
        queue_area_id = wpd.queue_area_id
    FROM workflow_plan_definition wpd
    WHERE wpd.id = mrg.plan_definition_id
        AND mrg.plan_definition_action_id IS NULL
        AND mrg.queue_token_location_id IS NOT NULL
    """,
    )
