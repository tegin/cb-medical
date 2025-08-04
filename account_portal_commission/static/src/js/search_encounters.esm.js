odoo.define("search_encounters.button", function (require) {
    const publicWidget = require("web.public.widget");
    const Dialog = require("web.Dialog");
    // Const _t = core._t;

    function fromField() {
        const code = document.createElement("input");
        code.setAttribute("name", "code");
        code.setAttribute("class", "form-control col-10 col-md-6");
        code.setAttribute("placeholder", "Internal Identifier");
        code.required = true;
        code.maxLength = 9;
        code.minLength = 9;
        return code;
    }

    function fixupView(oldNode) {
        let node = null;
        let code = null;
        switch (oldNode.nodeType) {
            case 1:
                if (oldNode.tagName === "field") {
                    node = fromField();
                    if (oldNode.getAttribute("name") === "code") {
                        code = node;
                        break;
                    }
                    break;
                }
                node = document.createElement(oldNode.tagName);
                for (let i = 0; i < oldNode.attributes.length; ++i) {
                    const attr = oldNode.attributes[i];
                    node.setAttribute(attr.name, attr.value);
                }
                for (let j = 0; j < oldNode.childNodes.length; ++j) {
                    const [ch, co] = fixupView(oldNode.childNodes[j]);
                    if (co) {
                        code = co;
                    }
                    if (ch) {
                        node.appendChild(ch);
                    }
                }
                break;
            case 3:
            case 4:
                node = document.createTextNode(oldNode.data);
                break;
            default:
        }
        return [node, code];
    }

    class Button {
        constructor(parent, id, model, input_node, button_node) {
            this._parent = parent;
            this.text = button_node.getAttribute("string");
            this.record_id = id;
            this.model = model;
            this.classes = button_node.getAttribute("class") || null;
            this.action = button_node.getAttribute("name");
            this.input = input_node;
            if (button_node.getAttribute("special") === "cancel") {
                this.close = true;
                this.click = null;
            } else {
                this.close = false;
                // Because Dialog doesnt' call() click on the descriptor object
                this.click = this._click.bind(this);
            }
        }
        async _click() {
            await this.callAction(this.record_id, {code: this.input.value});
        }
        async callAction(id, update) {
            await this._parent._rpc({
                model: this.model,
                method: "write",
                args: [[id], {code: update.code}],
            });
            await this._parent
                ._rpc({model: this.model, method: this.action, args: [[id]]})
                .then(function (result) {
                    if (result.id === false) {
                        new Dialog(this, {
                            title: "Encounter Information",
                            size: "large",
                            $content: `<div><p>No encounter has been found for this internal identifier.</p></div>`,
                            buttons: [
                                {
                                    text: "Cancel",
                                    close: true,
                                },
                            ],
                        }).open();
                        return;
                    }
                    var contentText = `<div>
                                        <p><strong>Internal Identifier: </strong>${_.str.escapeHTML(
                                            result.internal_identifier
                                        )}</p>
                                    `;

                    if (result.commissions) {
                        contentText += `<p><strong>Related commissions: </strong>
                                    <table style="border-collapse: collapse; width: 100%;">
                                    <body>`;
                        for (const commission of result.commissions) {
                            contentText += `<tr>
                                            <td style="border: 1px solid black; padding: 4px;">${_.str.escapeHTML(
                                                commission.invoice
                                            )}</td>
                                            <td style="border: 1px solid black; padding: 4px;">${_.str.escapeHTML(
                                                commission.name
                                            )}</td>
                                            <td style="border: 1px solid black; padding: 4px;">${_.str.escapeHTML(
                                                commission.amount
                                            )}€</td>
                                        </tr>`;
                        }
                        contentText += `</body></table>`;
                    }
                    contentText += `</div>`;
                    new Dialog(this, {
                        title: "Encounter Information",
                        size: "medium",
                        $content: contentText,
                        buttons: [
                            {
                                text: "Cancel",
                                close: true,
                            },
                        ],
                    }).open();
                });
        }
    }

    publicWidget.registry.SearchEncountersButton = publicWidget.Widget.extend({
        selector: "#search_encounters",
        events: {
            click: "_onClick",
        },

        async _onClick(e) {
            e.preventDefault();

            const w = await this._rpc({
                model: "res.users",
                method: "action_open_wizard",
                args: [this.getSession().user_id],
            });

            const {res_model: model, res_id: wizard_id} = w;

            const doc = new DOMParser().parseFromString(
                document.getElementById("search_encounters_wizard_view").textContent,
                "application/xhtml+xml"
            );

            const xmlBody = doc.querySelector("sheet *");
            const [body, code] = fixupView(xmlBody);

            const buttons = [];
            for (const button of doc.querySelectorAll("footer button")) {
                buttons.push(new Button(this, wizard_id, model, code, button));
            }

            // Wrap in a root host of .modal-body otherwise it breaks our neat flex layout
            const $content = document.createElement("form");
            $content.appendChild(body);
            // Implicit submission by pressing [return] from within input
            var dialog = new Dialog(this, {$content, buttons}).open();

            $content.addEventListener("submit", (event) => {
                event.preventDefault();
                // Sadness: footer not available as normal element
                dialog.$footer.find(".btn-primary").click();
            });
        },
    });
});
