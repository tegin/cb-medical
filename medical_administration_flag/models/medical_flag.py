from odoo import api, fields, models


class MedicalFlag(models.Model):
    # FHIR Entity: Flag (https://www.hl7.org/fhir/flag.html)
    _name = "medical.flag"
    _description = "Medical Flag"
    _inherit = "medical.abstract"

    patient_id = fields.Many2one(
        string="Patient",
        comodel_name="medical.patient",
        required=True,
        readonly=True,
        ondelete="restrict",
        index=True,
        help="Patient name",
    )  # FHIR Field: subject
    active = fields.Boolean(store=True, compute="_compute_active")
    category_id = fields.Many2one("medical.flag.category", required=True)
    name = fields.Char(related="category_id.name", readonly=True, store=True)
    description = fields.Text(required=True)
    closure_date = fields.Datetime(readonly=True)
    closure_uid = fields.Many2one(
        "res.users", readonly=True, string="Closure user"
    )

    @api.model
    def _get_internal_identifier(self, vals):
        return self.env["ir.sequence"].next_by_code("medical.flag") or "/"

    @api.multi
    @api.depends("name", "internal_identifier")
    def name_get(self):
        result = []
        for record in self:
            name = "[%s]" % record.internal_identifier
            if record.name:
                name = "%s %s" % (name, record.name)
            result.append((record.id, name))
        return result

    @api.depends("closure_date")
    def _compute_active(self):
        for rec in self:
            rec.active = not bool(rec.closure_date)

    @api.multi
    def close(self):
        return self.write(
            {
                "closure_date": fields.Datetime.now(),
                "closure_uid": self.env.user.id,
            }
        )
