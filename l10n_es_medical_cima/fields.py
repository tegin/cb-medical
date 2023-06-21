from odoo.fields import Char


class UnaccentedChar(Char):
    column_format = "unaccent(%s)"
