# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name":"All In One Helpdesk | CRM Helpdesk | Sale Order Helpdesk | Purchase Helpdesk | Invoice Helpdesk | Helpdesk Timesheet | Helpdesk Support Ticket To Task",
    "author":"Hoi",
    "website":"http://www.softhealer.com",
    "support":"support@softhealer.com",
    "category":"Discuss",
    "license":"OPL-1",
    "summary":"Flexible HelpDesk Customizable Help Desk Service Desk HelpDesk With Stages Help Desk Ticket Management Helpdesk Email Templates Email Alias Email Helpdesk Chatter Sale Order With Helpdesk,Purchase Order With Helpdesk Invoice With Helpdesk Odoo",
    "description":"""Are you looking for fully flexible and customisable helpdesk in odoo? Our this apps almost contain everything you need for Service Desk, Technical Support Team, Issue Ticket System which include service request to be managed in Odoo backend. Support ticket will send by email to customer and admin. Customer can view their ticket from the website portal and easily see stage of the reported ticket. This desk is fully customizable clean and flexible. """,
    "version":"15.0.26",
    "depends": ["mail","portal","product","resource","sale_management","purchase","account","hr_timesheet","crm","project",],
    "data": [
        "security/sh_helpdesk_security.xml",
        "security/ir.model.access.csv",
        "data/helpdesk_email_data.xml",
        "data/helpdesk_data.xml",
        "data/helpdesk_cron_data.xml",
        "data/helpdesk_stage_data.xml",
        "views/helpdesk_menu.xml",
        "views/helpdesk_sla_policies.xml",
        "views/helpdesk_alarm.xml",
        "data/helpdesk_reminder_cron.xml",
        "data/helpdesk_reminder_mail_template.xml",
        "views/helpdesk_team_view.xml",
        "views/helpdesk_ticket_type_view.xml",
        "views/helpdesk_subject_type_view.xml",
        "views/helpdesk_tags_view.xml",
        "views/helpdesk_stages_view.xml",
        "views/helpdesk_category_view.xml",
        "views/helpdesk_subcategory_view.xml",
        "views/helpdesk_priority_view.xml",
        "views/helpdesk_config_settings_view.xml",
        "views/helpdesk_ticket_view.xml",
        "views/sh_report_helpdesk_ticket_template.xml",
        "views/sh_helpdeks_report_portal.xml",
        "views/report_views.xml",
        "views/sh_ticket_feedback_template.xml",
        "views/ticket_dashboard_templates.xml",
        "views/res_users.xml",
        "views/helpdesk_merge_ticket_action.xml",
        "views/helpdesk_ticket_multi_action_view.xml",
        "views/helpdesk_ticket_update_wizard_view.xml",
        "views/helpdesk_ticket_portal_template.xml",
        "views/helpdesk_ticket_megre_wizard_view.xml",
        "views/helpdesk_ticket_task_info.xml"
    ],
    'assets': {
        'web.assets_backend': [
            # TICKET DASHBOARD
            'rt_helpdesk/static/src/components/ticket_dashboard.js',
            'rt_helpdesk/static/src/components/ticket_dashboard.xml',
            'rt_helpdesk/static/src/components/ticket_dashboard.scss',

            # TICKET LIST VIEW
            'rt_helpdesk/static/src/views/list.js',
            'rt_helpdesk/static/src/views/list.xml',

            # TICKET KANBAN VIEW
            'rt_helpdesk/static/src/views/kanban.js',
            'rt_helpdesk/static/src/views/kanban.xml',
            'rt_helpdesk/static/src/views/kanban.scss',

            # TICKET FIELD WIDGET 2
            'rt_helpdesk/static/src/fields/ticket_list_widget.js',
            'rt_helpdesk/static/src/fields/ticket_list_widget.xml',    

        ],
    },                     
    "application":
    True,
    "auto_install":
    False,
    "installable":
    True,
    'images': [
        'static/description/background.png',
    ],
    "price":
    100,
    "currency":
    "EUR"
}
