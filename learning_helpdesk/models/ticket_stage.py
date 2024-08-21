# -*- coding: utf-8 -*-

from odoo import api, fields, models

class Stage(models.Model):
    """ 
    Model for ticket stages. 
    """
    _name = "rt.helpdesk.ticket.stage"
    _description = "Ticket Stages"
    _rec_name = 'name'
    _order = "sequence asc"


    name = fields.Char('Stage Name', required=True, translate=True)
    partner_stage_name = fields.Char('Customer Stage Name', required=True, translate=True)    
    sequence = fields.Integer('Sequence', default=1, help="Used to order stages. Lower is better.")
    mail_template_id = fields.Many2one('mail.template', string='Email Template', domain=[('model', '=', 'rt.helpdesk.ticket')],
        help="If set, an email will be sent to the customer when the ticket reaches this stage.")
    fold = fields.Boolean('Folded in Kanban', help="This stage is folded in the kanban view.")

    is_opt_out_direction_flow = fields.Boolean(string='Opt Out direction flow?',
                             help='When an email will be sent to the customer when the ticket reaches this stage.At that time direction will not change to outgoing', 
                             default=False) 
    
    is_closed = fields.Boolean('Closing Stage', help="Tickets in this stage are considered as closed.")
    
    description = fields.Text(translate=True)    
    
    color_html = fields.Char(
        string='Color',
        help="Here you can set a specific HTML color index (e.g. #ff0000) to display the color in portal and kanban view")
        
    partner_stage_color_html = fields.Char(
        string='Customer Stage Color',
        help="Here you can set a specific HTML color index (e.g. #ff0000) to display the color in customer portal")
    