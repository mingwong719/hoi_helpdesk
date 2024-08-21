# -*- coding: utf-8 -*-

from odoo import api, fields, models
import ast

class Team(models.Model):
    """ 
    Model for helpdesk teams. 
    """
    _name = "rt.helpdesk.ticket.team"
    _inherit = ['mail.alias.mixin','mail.thread', 'mail.activity.mixin']
    _description = "Helpdesk Team"
    _rec_name = 'name'
    _order = "sequence, name, id"


    name = fields.Char('Helpdesk Team', required=True, translate=True)
    sequence = fields.Integer('Sequence', default=1, help="Used to order teams. Lower is better.")

    active = fields.Boolean(default=True, help="If the active field is set to false, it will allow you to hide the team without removing it.")

    user_id = fields.Many2one('res.users', string='Team Leader')


    description = fields.Html('About Team', translate=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    color = fields.Integer('Color Index', default=1)

    default_ticket_type_id = fields.Many2one('rt.helpdesk.ticket.type', 
        string='Default Ticket Type', 
        ondelete="set null")
        
    default_tag_ids = fields.Many2many(
        'rt.helpdesk.ticket.tag', 'rt_helpdesk_ticket_team_tag_rel', 'team_id', 'tag_id', string='Default Tags',
        help="Classify and analyze your ticket categories like: Problem, Service")    
        
    default_origin_id = fields.Many2one('rt.helpdesk.ticket.origin', 'Default Origin', index=True, ondelete='set null')
    

    def _default_domain_member_ids(self):
        return [('groups_id', 'in', self.env.ref('rt_helpdesk.rt_helpdesk_group_helpdesk_user').id)]


    member_ids = fields.Many2many('res.users', string='Team Members', domain=lambda self: self._default_domain_member_ids(), default=lambda self: self.env.user, required=True)



    # ------------------------------------------------------------
    # MESSAGING
    # ------------------------------------------------------------

    alias_id = fields.Many2one(help="Email alias for this helpdesk team. New emails will automatically create new ticket assigned to the team.")
    

    alias_email_from = fields.Char(compute='_compute_alias_email_from')

    def _compute_alias_email_from(self):
        res = self._notify_get_reply_to()
        for team in self:
            team.alias_email_from = res.get(team.id, False)

    def _alias_get_creation_values(self):
        values = super(Team, self)._alias_get_creation_values()
        values['alias_model_id'] = self.env['ir.model']._get('rt.helpdesk.ticket').id
        if self.id:
            values['alias_defaults'] = defaults = ast.literal_eval(self.alias_defaults or "{}")
            defaults['team_id'] = self.id
        return values