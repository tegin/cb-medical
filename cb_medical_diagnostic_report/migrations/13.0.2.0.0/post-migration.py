from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    group = env.ref(
        "medical_diagnostic_report.group_medical_diagnostic_report_template_manager"
    )
    new_group = env.ref(
        "cb_medical_diagnostic_report.group_medical_template_manager_all"
    )
    groups = env["res.groups"].search([("implied_ids", "=", group.id)])
    groups.write({"implied_ids": [(4, new_group.id)]})
    group.users.write({"groups_id": [(4, new_group.id)]})
