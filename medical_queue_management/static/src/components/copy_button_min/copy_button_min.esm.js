/** @odoo-module */

import {CopyClipboardButtonField} from "@web/views/fields/copy_clipboard/copy_clipboard_field";
import {registry} from "@web/core/registry";

export class CopyClipboardButtonMinField extends CopyClipboardButtonField {
    setup() {
        super.setup();
        this.copyText = "";
    }
}

registry.category("fields").add("CopyClipboardButtonMin", CopyClipboardButtonMinField);
