# Copyright 2023 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, tools


class ReportPosPayment(models.Model):
    _name = "report.pos.payment"
    _description = "Point Of Sale Payment Analysis"
    _auto = False
    _rec_name = "date"
    _order = "date desc"

    date = fields.Date()
    amount = fields.Monetary(currency_field="currency_id")
    encounter_id = fields.Many2one("medical.encounter")
    currency_id = fields.Many2one("res.currency")
    company_id = fields.Many2one("res.company")
    session_id = fields.Many2one("pos.session")
    config_id = fields.Many2one("pos.config")

    def _select_query(self):
        return ",".join(
            "%s as %s" % (value, field)
            for field, value in self._select_query_fields().items()
        )

    def _select_query_fields(self):
        return {
            "id": "posp.id",
            "date": "posp.payment_date",
            "amount": "posp.amount",
            "encounter_id": "posp.encounter_id",
            "company_id": "poso.company_id",
            "currency_id": "COALESCE(aj.currency_id, rc.currency_id)",
            "session_id": "poss.id",
            "config_id": "posc.id",
        }

    def _from_query(self):
        return """
            pos_payment as posp
            INNER JOIN pos_session as poss ON poss.id = posp.session_id
            INNER JOIN pos_payment_method as pospm ON pospm.id = posp.payment_method_id
            INNER JOIN pos_config as posc ON posc.id = poss.config_id
            INNER JOIN pos_order as poso ON poso.id = posp.pos_order_id
            INNER JOIN res_company as rc ON rc.id = poso.company_id
            LEFT JOIN account_journal as aj ON aj.id = poso.sale_journal
        """

    def _where_query(self):
        return "TRUE"

    def _query(self):
        return "SELECT %s FROM %s WHERE %s" % (
            self._select_query(),
            self._from_query(),
            self._where_query(),
        )

    def init(self):
        # self._table = sale_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(
            """CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query())
        )
