odoo.define("diagnostic_report.DiagnosticReportRenderer", function(require) {
    "use strict";

    var FormRenderer = require("web.FormRenderer");

    var DiagnosticReportRenderer = FormRenderer.extend({
        events: _.extend({}, FormRenderer.prototype.events, {
            paste: "_onPaste",
        }),
        _onPaste: function(e) {
            if (this.mode !== "readonly") {
                return;
            }
            this.trigger_up("paste_file", {
                clipboardData: e.originalEvent.clipboardData,
            });
        },
    });

    return DiagnosticReportRenderer;
});
