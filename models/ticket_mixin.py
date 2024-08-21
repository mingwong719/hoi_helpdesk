#+ -*- coding: utf-8 -*-


import logging
from odoo import api, fields, models
_logger = logging.getLogger(__name__)


class rt_helpdesk_ticket_mixin(models.AbstractModel):
    _name = 'rt.helpdesk.ticket.mixin'
    _description = 'Ticket Mixin'


    rt_helpdesk_ticket_ids = fields.One2many(
        comodel_name='rt.helpdesk.ticket', 
        inverse_name='res_id', 
        string='Tickets',
        auto_join=True,
        copy=False,
        groups="rt_helpdesk.rt_helpdesk_group_helpdesk_user")
    
    rt_helpdesk_direction = fields.Selection([
        ('incoming', 'Incoming'),
        ('outgoing', 'Outgoing')
    ],  string='Ticket Direction',
        compute='_compute_rt_helpdesk_direction',
        search='_search_rt_helpdesk_direction',
        groups="rt_helpdesk.rt_helpdesk_group_helpdesk_user",    
    )
        
        
    def _search_rt_helpdesk_direction(self, operator, operand):
        return [('rt_helpdesk_ticket_ids.direction', operator, operand)]

    @api.depends('rt_helpdesk_ticket_ids.direction')
    def _compute_rt_helpdesk_direction(self):
        for record in self:
            direction = record.rt_helpdesk_ticket_ids.mapped('direction')
            if 'incoming' in direction:
                record.rt_helpdesk_direction = 'incoming'
            elif 'outgoing' in direction:
                record.rt_helpdesk_direction = 'outgoing'
            else:
                record.rt_helpdesk_direction = False