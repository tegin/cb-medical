from datetime import timedelta, datetime, date
import pytz
from odoo import api, models, fields, _
from odoo.exceptions import UserError


def parse_atom(parse, minmax):
    parse = parse.strip()
    increment = 1
    if parse == '*':
        return set(range(minmax[0], minmax[1] + 1))
    elif parse.isdigit():
        # A single number still needs to be returned as a set
        value = int(parse)
        if minmax[0] <= value <= minmax[1]:
            return set((value,))
        else:
            raise UserError(_("\"%s\" is not within valid range.") % parse)
    elif '-' in parse or '/' in parse:
        divide = parse.split('/')
        subrange = divide[0]
        if len(divide) == 2:
            # Example: 1-3/5 or */7 increment should be 5 and 7 respectively
            increment = int(divide[1])

        if '-' in subrange:
            # Example: a-b
            prefix, suffix = [int(n) for n in subrange.split('-')]
            if prefix < minmax[0] or suffix > minmax[1]:
                raise UserError(_("\"%s\" is not within valid range.") % parse)
        elif subrange == '*':
            # Include all values with the given range
            prefix, suffix = minmax
        else:
            raise UserError(_("Unrecognized symbol \"%s\"") % subrange)

        if prefix < suffix:
            # Example: 7-10
            return set(range(prefix, suffix + 1, increment))
        else:
            # Example: 12-4/2; (12, 12 + n, ..., 12 + m*n) U (n_0, ..., 4)
            noskips = list(range(prefix, minmax[1] + 1))
            noskips += list(range(minmax[0], suffix + 1))
            return set(noskips[::increment])
    else:
        raise UserError(_("Atom \"%s\" not in a recognized format.") % parse)


class MedicalGuardPlan(models.Model):
    _name = 'medical.guard.plan'

    start_time = fields.Float(required=True)
    end_time = fields.Float(required=True)
    location_id = fields.Many2one(
        'res.partner',
        domain=[('is_center', '=', True), ('guard_journal_id', '!=', False)],
        required=True,
    )
    product_id = fields.Many2one(
        'product.product',
        required=True,
        domain=[('type', '=', 'service')],
    )
    active = fields.Boolean(
        required=True,
        default=True,
    )
    weekday = fields.Char(
        required=True,
        default='*',
        help="Use it in order to filter the weekdays, where 0 is monday "
             "and 6 sunday. You could use 0-4 in order to select Monday to "
             "Friday. Use * for all.",
    )
    monthday = fields.Char(
        required=True,
        default='*',
        help="Use it in order to filter the day of the month. Use * for all.",
    )
    month = fields.Char(
        required=True,
        default='*',
        help="Use it in order to filter the month. Use * for all.",
    )

    def _check(self, value, expr_vals, minmax):
        for expr in expr_vals.split(','):
            if bool(value in parse_atom(expr, minmax)):
                return True
        return False

    @api.multi
    def check_date(self, date_str):
        date = date_str
        if isinstance(date_str, str):
            date = fields.Date.from_string(date_str)
        if not self._check(date.weekday(), self.weekday, (0, 6)):
            return False
        if not self._check(date.month, self.month, (1, 12)):
            return False
        if not self._check(date.day, self.monthday, (1, 31)):
            return False
        return True

    def _prepare_guard_vals(self, str_date):
        date_date = str_date
        if isinstance(str_date, str):
            date_date = fields.Date.from_string(str_date)
        datetime_date = date_date
        tz = pytz.timezone(self.env.context.get('tz') or 'UTC')
        if isinstance(date_date, date):
            datetime_date = tz.localize(datetime(
                date_date.year, date_date.month, date_date.day))
        return {
            'date': fields.Datetime.to_string(
                (datetime_date + timedelta(hours=self.start_time)).astimezone(
                    tz=None)),
            'end_date': fields.Datetime.to_string(
                (datetime_date + timedelta(hours=self.end_time)).astimezone(
                    tz=None)),
            'location_id': self.location_id.id,
            'product_id': self.product_id.id,
            'plan_guard_id': self.id,
        }

    @api.multi
    def apply_plan(self, date):
        return self.env['medical.guard'].create(self._prepare_guard_vals(date))
