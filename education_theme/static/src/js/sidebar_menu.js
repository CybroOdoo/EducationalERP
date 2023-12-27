/** @odoo-module **/
import { NavBar} from "@web/webclient/navbar/navbar";
import { patch } from "@web/core/utils/patch";
// Patch navbar for adding new sidebar functionality
patch(NavBar.prototype, {
    // Toggle sidebar on click
    openSidebar(ev) {
        var $el = $(ev.target).parents().find('header #sidebar_panel')
        var action = $(ev.target).parents().find('body .o_action_manager')
        if (!$(ev.target).hasClass('opened')) {
            $el.show()
            $(ev.target).toggleClass('opened')
            action.css({
                'margin-left': '270px',
                'transition': 'all .1s linear'
            });
        } else {
            $el.hide()
            $(ev.target).toggleClass('opened')
            action.css({'margin-left': '0px'});
        }
    },
    // Hide sidebar on clicking app menu
    clickSidebar(ev) {
        var $el = $(ev.target).parents().find('header #sidebar_panel')
        var action = $(ev.target).parents().find('body .o_action_manager')
        $el.css({'display': 'none'});
        action.css({'margin-left': '0px'});
    },
});
