odoo.define("diagnostic_report.DiagnosticReportRenderer", function (require) {
    "use strict";

    var FormRenderer = require("web.FormRenderer");

    var DiagnosticReportRenderer = FormRenderer.extend({
        events: _.extend({}, FormRenderer.prototype.events, {
            paste: "_onPaste",
            click: "_onClickPaste",
        }),
        _onClickPaste: function (e) {
            var $pasteEl = this.$el.find(".o_diagnostic_report_paste_image_parent");
            if ($(e.target).hasClass("o_diagnostic_report_paste_image")) {
                $pasteEl.addClass("selected");
                this.paste_selected = true;
            } else {
                $pasteEl.removeClass("selected");
                this.paste_selected = false;
            }
        },
        _onPaste: function (e) {
            if (this.paste_selected) {
                this.trigger_up("paste_file", {
                    clipboardData: e.originalEvent.clipboardData,
                });
                this.$el
                    .find(".o_diagnostic_report_paste_image_parent")
                    .removeClass("selected");
                this.paste_selected = false;
            }
        },
    });

    return DiagnosticReportRenderer;
});
