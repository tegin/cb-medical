# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StorageFile(models.Model):
    _inherit = "storage.file"

    file_type = fields.Selection(
        selection_add=[("diagnostic_report_image", "Diagnostic Report Image")]
    )
