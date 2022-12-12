# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models
from odoo.osv import expression


class MedicalLaboratoryService(models.Model):
    _name = "medical.laboratory.service"
    _description = "Laboratory service"
    _rec_name = "name"

    code = fields.Char(required=True)
    name = fields.Char()
    delay = fields.Integer()
    laboratory_code = fields.Char(required=True)
    service_price_ids = fields.One2many(
        "medical.laboratory.service.price",
        inverse_name="laboratory_service_id",
        readonly=True,
    )
    active = fields.Boolean(default=True, required=True)

    _sql_constraints = [
        (
            "unique_laboratory_code",
            "UNIQUE(laboratory_code)",
            "Laboratory Code must be unique",
        )
    ]

    @api.depends("code", "name")
    def _compute_display_name(self):
        return super()._compute_display_name()

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        """Include commercial name in direct name search."""
        args = expression.normalize_domain(args)
        for arg in args:
            if isinstance(arg, (list, tuple)):
                if arg[0] == "name" or arg[0] == "display_name":
                    index = args.index(arg)
                    args = args[:index] + ["|", ("code", arg[1], arg[2])] + args[index:]
                    break
        return super().search(
            args, offset=offset, limit=limit, order=order, count=count
        )

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        """Give preference to commercial names on name search"""
        if not args:
            args = []
        recs = self.search([("code", operator, name)] + args, limit=limit)
        res = recs.name_get()
        if limit:
            limit_rest = limit - len(recs)
        else:  # pragma: no cover
            # limit can be 0 or None representing infinite
            limit_rest = limit
        if limit_rest or not limit:
            args += [("id", "not in", recs.ids)]
            res += super().name_search(
                name, args=args, operator=operator, limit=limit_rest
            )
        return res

    def name_get(self):
        result = []
        orig_name = dict(super().name_get())
        for rec in self:
            name = orig_name[rec.id]
            code = rec.code
            if code:
                name = "[{}] {}".format(code, name)
            result.append((rec.id, name))
        return result


class MedicalLaboratoryServicePrice(models.Model):
    _name = "medical.laboratory.service.price"
    _description = "Laboratory service price list"

    laboratory_service_id = fields.Many2one("medical.laboratory.service", required=True)
    laboratory_code = fields.Char(required=True, string="Coverage code")
    amount = fields.Float(required=True)
    cost = fields.Float()

    _sql_constraints = [
        (
            "unique_code",
            "UNIQUE(laboratory_code, laboratory_service_id)",
            "Code must be unique on a service",
        )
    ]
