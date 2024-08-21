/** @odoo-module **/

import { registry } from "@web/core/registry";
import { usePopover } from "@web/core/popover/popover_hook";
import { Component, useEnv, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

import { _t } from "@web/core/l10n/translation";
// import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

import { deserializeDateTime } from "@web/core/l10n/dates";
import { groupBy, sortBy, unique } from "@web/core/utils/arrays";

import { computeDelay } from "@mail/utils/common/dates";

class RtHelpdeskTicketListPopover extends Component {}
RtHelpdeskTicketListPopover.template = "rt_helpdesk.RtHelpdeskTicketListPopover";

class RtHelpdeskTicketButton extends Component {

    // also used in children, in particular in ActivityButton
    static fieldDependencies = [
        { name: "rt_helpdesk_direction", type: "selection", selection: [] },
    ];
    static props = standardFieldProps;
    static template = "rt_helpdesk.RtHelpdeskTicketButton";



    setup() {
        super.setup();
        // const position = localization.direction === "rtl" ? "bottom" : "right";
        this.popover = usePopover(RtHelpdeskTicketListPopover, { position: "bottom-start" });
        this.buttonRef = useRef("button");
        this.orm = useService("orm");
        this.user = useService("user");
        this.actionService = useService("action");
        // this.popover = usePopover(RtHelpdeskTicketListPopover, { position });
    }

    get title() {
        return _t("Show Tickets");
    }

    get buttonClass() {
        const classes = ["fa fa-life-ring"];
        switch (this.props.record.data.rt_helpdesk_direction) {
            case "incoming":
                classes.push("text-danger");
                break;
            case "outgoing":
                classes.push("text-success");
                break;
            case false:
                classes.push("text-warning");
                break;
        }
        return classes.join(" ");
    }


    get summaryText() {
        const { rt_helpdesk_ticket_ids} = this.props.record.data;
        if (rt_helpdesk_ticket_ids.records.length) {
            return rt_helpdesk_ticket_ids.records.length;
        }
        return undefined;
    }


    delayLabel(date) {
        const diff = computeDelay(date);
        if (diff === 0) {
            return _t("Today");
        } else if (diff === -1) {
            return _t("Yesterday");
        } else if (diff < 0) {
            return _t("%s days overdue", Math.round(Math.abs(diff)));
        } else if (diff === 1) {
            return _t("Tomorrow");
        } else {
            return _t("Due in %s days", Math.round(Math.abs(diff)));
        }
    }

    dateDeadlineFormatted(date_deadline) {
        return luxon.DateTime.fromISO(date_deadline).toLocaleString(
            luxon.DateTime.DATE_SHORT
        );
    }

    createDateFormatted(create_date) {
        return deserializeDateTime(create_date).toLocaleString(
            luxon.DateTime.DATETIME_SHORT_WITH_SECONDS
        );
    }


    /**
     * @override
     */
    async getPopoverProps() {
        const list_tickets_dic = this.props.record.data.rt_helpdesk_ticket_ids.currentIds
            ? await this.orm.silent.call(
                "rt.helpdesk.ticket",
                "ticket_field_widget_format",
                [this.props.record.data.rt_helpdesk_ticket_ids.currentIds],
                {
                    context: this.user.user_context,
                }
            )
            : [];

        for (const ticket of list_tickets_dic) {
            ticket.create_date = this.createDateFormatted(ticket.create_date);
            
            let toDisplay = "";
            if (ticket.date_deadline) {
                toDisplay = this.delayLabel(ticket.date_deadline);
                ticket.date_deadline = this.dateDeadlineFormatted(ticket.date_deadline);
            }
            ticket.label_delay = toDisplay;
        }
        const sorted_list_tickets_dic = sortBy(list_tickets_dic, "create_date").reverse();
        return groupBy(sorted_list_tickets_dic, "direction");
    }

    
    async onClick(ev) {
        var target =  ev.currentTarget;
        if (this.popover.isOpen) {
            this.popover.close();
        } else {
            var records = await this.getPopoverProps();
            var rt_helpdesk_direction_selection = {};   
            for (const [type, label] of this.props.record.fields.rt_helpdesk_direction.selection) {
                rt_helpdesk_direction_selection[type] = label;
            }
            this.popover.open(target, {
                records:records,
                //widget: this,
                rt_helpdesk_direction_selection:rt_helpdesk_direction_selection,
                _onEditTicket: this.editTicket.bind(this),
                _onOpenTicketsListView: this.openTicketsListView.bind(this),

            });     
        }
    }


    async openTicketsListView() {
        this.popover.close();        

        var partner_id = false;
        if (this.props.record.data.partner_id) {
            partner_id = this.props.record.data.partner_id[0 /* id */];
        }

        var domain = [
            ["res_id", "=", parseInt(this.props.record.resId)],
            ["res_model", "=", this.props.record.resModel],
        ];
        var action = {
            type: "ir.actions.act_window",
            name: _t("Tickets"),
            res_model: "rt.helpdesk.ticket",
            view_mode: "list",
            views: [
                [false, "list"],
                [false, "kanban"],
                [false, "form"],
                [false, "calendar"],
                [false, "pivot"],
                [false, "graph"],
                [false, "activity"],
            ],
            target: "current",
            domain: domain,
            context: {
                ...this.user.context,
                default_active_model: this.props.record.resModel,
                default_active_id: this.props.record.resId,
                default_partner_id: partner_id,
                default_res_id: this.props.record.resId,
                default_res_model:  this.props.record.resModel,                       
            },
        };
        this.actionService.doAction(action);
    }

    async editTicket(ticketId) {
        if (!ticketId) {
            await this.props.record.save();
        }
        this.popover.close();
        var partner_id = false;
        if (this.props.record.data.partner_id) {
            partner_id = this.props.record.data.partner_id[0 /* id */];
        }
        this.actionService.doAction(
            {
                type: "ir.actions.act_window",
                target: "current",
                res_model: "rt.helpdesk.ticket",
                views: [[false, "form"]],
                res_id: ticketId || false,                
                context: {
                    ...this.user.context,
                    default_active_model: this.props.record.resModel,
                    default_active_id: this.props.record.resId,              
                    default_partner_id: partner_id,
                    default_res_id: this.props.record.resId,
                    default_res_model:  this.props.record.resModel,                          
                },
            }
            );        
    }
    
    
}

// RtHelpdeskTicketButton.template = "rt_helpdesk.RtHelpdeskTicketButton";
registry.category("fields").add("rt_helpdesk_list_ticket_field", {
    component: RtHelpdeskTicketButton,
    fieldDependencies: RtHelpdeskTicketButton.fieldDependencies,    
    supportedTypes: ["one2many"],    
   // displayName: _t("Ticket"),    
});


