# Copyright 2022 Creu Blanca 2022
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models
from odoo.osv.expression import get_unaccent_wrapper

from ..fields import UnaccentedChar

_logger = logging.getLogger(__name__)


class MedicalProductTemplate(models.Model):

    _inherit = "medical.product.template"

    product_tmpl_commercial_ids = fields.One2many(
        "medical.product.template.commercial",
        inverse_name="product_tmpl_id",
        auto_join=True,
    )
    product_commercial_ids = fields.One2many(
        "medical.product.product.commercial",
        inverse_name="product_tmpl_id",
        auto_join=True,
    )
    product_tmpl_commercial_count = fields.Integer(
        compute="_compute_product_tmpl_commercial_ids"
    )
    unaccented_name = UnaccentedChar(
        related="name", store=True, index=True, string="Unnacented name"
    )
    cima_ref = fields.Char()
    can_drive = fields.Boolean(default=True)
    in_patient = fields.Boolean(compute="_compute_in_patient", store=True)

    @api.depends("product_tmpl_commercial_ids.in_patient")
    def _compute_in_patient(self):
        for record in self:
            record.in_patient = any(
                record.product_tmpl_commercial_ids.mapped("in_patient")
            )

    @api.depends("product_tmpl_commercial_ids")
    def _compute_product_tmpl_commercial_ids(self):
        for rec in self:
            rec.product_tmpl_commercial_count = len(rec.product_tmpl_commercial_ids)

    def action_view_product_tmpl_commercial_ids(self):
        action = self.env.ref(
            "l10n_es_medical_cima." "medical_product_template_commercial_act_window"
        ).read()[0]
        action["domain"] = [("product_tmpl_id", "=", self.id)]
        if len(self.product_tmpl_commercial_ids) == 1:
            view = (
                "l10n_es_medical_cima." "medical_product_template_commercial_form_view"
            )
            form_view = [(self.env.ref(view).id, "form")]
            if "views" in action:
                action["views"] = form_view + [
                    (state, view) for state, view in action["views"] if view != "form"
                ]
            else:
                action["views"] = form_view
            action["res_id"] = self.product_tmpl_commercial_ids.id
        return action

    def _name_search_query(self, name, args, operator):
        if args is None:
            args = []
        unaccent = get_unaccent_wrapper(self.env.cr)
        from_clause, where_clause, where_clause_params = self._where_calc(
            args
        ).get_sql()
        from_str = from_clause if from_clause else self._table
        where_str = where_clause and (" WHERE %s AND " % where_clause) or " WHERE "
        query = """
                SELECT DISTINCT {table}.id
                FROM {from_str}
                LEFT JOIN "medical_product_template_commercial"
                ON "medical_product_template_commercial".
                "product_tmpl_id"="{table}"."id"
                LEFT JOIN "medical_product_product_commercial"
                ON "medical_product_product_commercial".
                "product_tmpl_id"="{table}"."id"
                {where} (
                    {rec_name} {operator} {percent} OR
                    {laboratory_product_name} {operator} {percent} OR
                    {product_code} {operator} {percent}
                )
                ORDER BY {order}
                """.format(
            table=self._table,
            from_str=from_str,
            where=where_str,
            rec_name='"{}"."{}"'.format(self._table, "unaccented_name"),
            percent=unaccent("%s"),
            operator=operator,
            order=",".join(
                [
                    '"{}"."{}"'.format(self._table, order)
                    for order in self._order.split(",")
                ]
            ),
            laboratory_product_name='"medical_product_template_commercial".'
            '"unaccented_laboratory_product_name"',
            product_code='"medical_product_product_commercial"."unaccented_code"',
        )
        where_clause_params += [
            name,
            name,
            name,
        ]
        return query, where_clause_params

    @api.model
    def _name_search(
        self,
        name="",
        args=None,
        operator="ilike",
        limit=100,
        name_get_uid=None,
    ):
        if name and operator in ("=", "ilike", "=ilike", "like", "=like"):
            self = self.with_user(name_get_uid or self.env.uid)
            self.check_access_rights("read")
            search_name = name
            if operator in ("ilike", "like"):
                search_name = "%%%s%%" % name
            if operator in ("=ilike", "=like"):
                operator = operator[1:]
            query, where_clause_params = self._name_search_query(
                search_name, args, operator
            )
            if limit:
                query += " limit %s"
                where_clause_params.append(limit)
            self.env.cr.execute(query, where_clause_params)
            ids = [row[0] for row in self.env.cr.fetchall()]
            if ids:
                return ids
            else:
                return []
        return super()._name_search(
            name,
            args,
            operator=operator,
            limit=limit,
            name_get_uid=name_get_uid,
        )


class MedicalProductProduct(models.Model):

    _inherit = "medical.product.product"

    product_commercial_ids = fields.One2many(
        "medical.product.product.commercial", inverse_name="medical_product_id"
    )

    product_commercial_count = fields.Integer(compute="_compute_product_commercial_ids")
    cima_ref = fields.Char()
    active = fields.Boolean(compute="_compute_active", store=True)

    @api.depends("product_commercial_ids.active")
    def _compute_active(self):
        for record in self:
            record.active = any(record.product_commercial_ids.mapped("active"))

    @api.depends("product_commercial_ids")
    def _compute_product_commercial_ids(self):
        for rec in self:
            rec.product_commercial_count = len(rec.product_commercial_ids)

    def action_view_product_commercial_ids(self):
        action = self.env.ref(
            "l10n_es_medical_cima." "medical_product_product_commercial_act_window"
        ).read()[0]
        action["domain"] = [("medical_product_id", "=", self.id)]
        if len(self.product_commercial_ids) == 1:
            view = (
                "l10n_es_medical_cima." "medical_product_product_commercial_form_view"
            )
            form_view = [(self.env.ref(view).id, "form")]
            if "views" in action:
                action["views"] = form_view + [
                    (state, view) for state, view in action["views"] if view != "form"
                ]
            else:
                action["views"] = form_view
            action["res_id"] = self.product_commercial_ids.id
        return action
