/** @odoo-module */

import { registry } from "@web/core/registry";
import { kanbanView } from "@web/views/kanban/kanban_view";
import { KanbanRenderer } from "@web/views/kanban/kanban_renderer";
import { RTHelpdeskDashboard } from "@rt_helpdesk/components/ticket_dashboard";


export class RTHelpdeskKanbanRenderer extends KanbanRenderer {}

RTHelpdeskKanbanRenderer.template = "rt_helpdesk.RTHelpdeskKanbanRenderer";
RTHelpdeskKanbanRenderer.components = Object.assign({}, KanbanRenderer.components, { RTHelpdeskDashboard });

export const RTHelpdeskKanbanTicketDashboard = {
    ...kanbanView,
    Renderer: RTHelpdeskKanbanRenderer,
};

registry.category("views").add("rt_helpdesk_kanban_ticket_dashboard", RTHelpdeskKanbanTicketDashboard);


