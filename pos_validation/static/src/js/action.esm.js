/** @odoo-module **/

import {registry} from "@web/core/registry";

/**
 * Handle 'ir.actions.act_multi' action
 * @param {object} action see _handleAction() parameters
 * @returns {$.Promise}
 */

async function executeMultiAction({env, action}) {
    const finalAction = env.services.action.currentController.action;
    finalAction.res_id = action.res_id;
    return env.services.action.doAction(finalAction, {
        stackPosition: "replaceCurrentAction",
    });
}

registry
    .category("action_handlers")
    .add("ir.actions.act_client_load_new", executeMultiAction);
