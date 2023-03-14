# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class IrActionsActMulti(models.Model):
    _name = "ir.actions.act_client_load_new"
    _description = "Action Load new record"
    _inherit = "ir.actions.actions"
    _table = "ir_actions"

    type = fields.Char(default="ir.actions.act_client_load_new")
