/** @odoo-module **/

import {Component} from "@odoo/owl";
import {registry} from "@web/core/registry";
import {Dialog} from "@web/core/dialog/dialog";

export class RestrictedMenuDialog extends Component {
    static template = "education_core.RestrictedMenuDialog";
    static components = {Dialog};

    setup() {
        this.adminEmail = "info@cybrosys.com";
        this.mailToUrl = `mailto:${this.adminEmail}?subject=Access Request`;
    }

    _onClose() {
        this.props.close();
    }
}

// Client action wrapper to render inside a Dialog popup
export function restrictedMenuClientAction(env, action) {
    env.services.dialog.add(RestrictedMenuDialog, {
        title: "Access Restricted",
    });
}

// Register the client action tag
registry.category("actions").add("action_restricted_menu_popup", restrictedMenuClientAction);