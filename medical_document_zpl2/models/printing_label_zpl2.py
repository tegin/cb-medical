from odoo import _, exceptions, models


class PrintingLabelZpl2(models.Model):
    _inherit = "printing.label.zpl2"

    def render_label(self, record, page_count=1, **extra):
        res = ""
        for label in self:
            if record._name != label.model_id.model:
                raise exceptions.UserError(
                    _("This label cannot be used on %s") % record._name
                )
            if len(res) > 0:
                res += "\n"
            # Send the label to printer
            res += label._generate_zpl2_data(
                record, page_count=page_count, **extra
            ).decode("utf-8")
        return res
