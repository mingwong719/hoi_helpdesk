/** @odoo-module */

import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";
import { ListRenderer } from "@web/views/list/list_renderer";

import { RTHelpdeskDashboard } from "@rt_helpdesk/components/ticket_dashboard";


export class RTHelpdeskListRenderer extends ListRenderer {}

RTHelpdeskListRenderer.template = "rt_helpdesk.RTHelpdeskListRenderer";
RTHelpdeskListRenderer.components = Object.assign({}, ListRenderer.components, { RTHelpdeskDashboard });

export const RTHelpdeskListTicketDashboard = {
    ...listView,
    Renderer: RTHelpdeskListRenderer,
};

registry.category("views").add("rt_helpdesk_list_ticket_dashboard", RTHelpdeskListTicketDashboard);

