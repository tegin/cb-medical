/** @odoo-module */

import {Component} from "@odoo/owl";
import {Dialog} from "@web/core/dialog/dialog";
import {_lt} from "@web/core/l10n/translation";
import {evaluateExpr} from "@web/core/py_js/py";
import {registry} from "@web/core/registry";
import {standardWidgetProps} from "@web/views/widgets/standard_widget_props";
import {useService} from "@web/core/utils/hooks";

export class QueueTokenLocationAssignDialog extends Component {
    setup() {
        this.ui = useService("ui");
        this.orm = useService("orm");
        this.action = useService("action");
    }
    async assignFunction(itemId) {
        this.ui.block();
        try {
            await this.orm.call(
                this.props.record.resModel,
                this.props.assignFunction,
                [this.props.record.resIds, itemId],
                {context: this.props.context}
            );
            this.props.close();
            await this.action.doAction({type: "ir.actions.client", tag: "soft_reload"});
        } finally {
            this.ui.unblock();
        }
    }
}
QueueTokenLocationAssignDialog.template =
    "medical_queue_management.QueueTokenLocationAssignDialog";
QueueTokenLocationAssignDialog.props = {
    close: Function,
    data: Object,
    assignFunction: String,
    record: Object,
    context: Object,
    cancelLabel: {type: String, optional: true},
};
QueueTokenLocationAssignDialog.defaultProps = {
    cancelLabel: _lt("Cancel"),
};

QueueTokenLocationAssignDialog.components = {Dialog};

class QueueTokenLocationAssignGroup extends Component {
    setup() {
        this.ui = useService("ui");
        this.orm = useService("orm");
        this.dialog = useService("dialog");
    }
    get domain() {
        return evaluateExpr(this.props.domain, this.props.record.evalContext);
    }
    async onClick() {
        this.ui.block();
        const context = evaluateExpr(this.props.context, this.props.record.evalContext);
        const data = await this.orm.call(
            this.props.model,
            "name_search",
            ["", this.domain],
            {context}
        );
        this.ui.unblock();
        this.dialog.add(QueueTokenLocationAssignDialog, {
            data,
            record: this.props.record,
            assignFunction: this.props.function,
            context,
        });
    }
}

QueueTokenLocationAssignGroup.template =
    "medical_queue_management.QueueTokenLocationAssignGroup";
QueueTokenLocationAssignGroup.props = {
    ...standardWidgetProps,
    domain: String,
    context: String,
    model: String,
    function: String,
    title: String,
    class: String,
};
QueueTokenLocationAssignGroup.extractProps = ({attrs}) => {
    return {
        domain: attrs.domain,
        context: attrs.context,
        model: attrs.model,
        function: attrs.function,
        title: attrs.title,
        class: attrs.btnclass,
    };
};

registry
    .category("view_widgets")
    .add("queue_token_location_assign_group", QueueTokenLocationAssignGroup);
