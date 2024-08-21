# -*- coding: utf-8 -*-

from odoo import Command, models, fields, api, _


AVAILABLE_PRIORITIES = [
    ('0', 'Low'),
    ('1', 'Medium'),
    ('2', 'High'),
    ('3', 'Very High'),
]

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.addons.iap.tools import iap_tools
from odoo.addons.mail.tools import mail_validation
from odoo.addons.phone_validation.tools import phone_validation
from odoo.exceptions import UserError, AccessError
from odoo.osv import expression
from odoo.tools.translate import _
from odoo.tools import date_utils, email_re, email_split, is_html_empty

from odoo import SUPERUSER_ID

class rt_helpdesk_ticket(models.Model):
    _name = 'rt.helpdesk.ticket'
    _description = 'Helpdesk Ticket'
    _inherit = [
                'portal.mixin',
                'mail.thread.blacklist',
                'mail.thread.phone',
                'mail.activity.mixin',
                'mail.thread.cc',
                'mail.tracking.duration.mixin',                
               ]
    _primary_email = 'email_from'
    _rec_name = 'ticket_number'
    _order = 'direction'    
    _track_duration_field = 'stage_id'
        

            
    
    name = fields.Char("Subject", translate=True, 
                       required=True, help="Email subject for ticket sent via email")

    ticket_number = fields.Char(string='Ticket Number', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    #subject = fields.Char(string="Subject", translate=True)
    description_html = fields.Html(string="Description",translate=True)
    
    sequence = fields.Integer(string='Sequence',  index=True, default=10,
        help="Gives the sequence order when displaying a list of tickets.")
    priority = fields.Selection(selection=AVAILABLE_PRIORITIES,
        default=AVAILABLE_PRIORITIES[0][0],
        string='Priority', 
        index=True,
        tracking=True
        )
           
    ticket_type_id = fields.Many2one('rt.helpdesk.ticket.type', 
        string='Ticket Type', 
        ondelete="set null")
    
                
    active = fields.Boolean(default=True,
        help="If the active field is set to False, it will allow you to hide the ticket without removing it.")

    partner_id = fields.Many2one(
        'res.partner', string='Customer',
        change_default=True, 
        index=True, 
        tracking=True)       
    
    email_from = fields.Char(
        'Email', tracking=40, index=True,
        compute='_compute_email_from', inverse='_inverse_email_from', readonly=False, store=True)
    phone = fields.Char(
        'Phone', tracking=50,
        compute='_compute_phone', inverse='_inverse_phone', readonly=False, store=True)
    mobile = fields.Char(
        'Mobile', tracking=50,
        compute='_compute_mobile', inverse='_inverse_mobile', readonly=False, store=True)
    
 
    def _get_default_user_ids(self):
        return [(6, 0, [self.env.uid])]
 
    user_ids = fields.Many2many('res.users', relation='rt_helpdesk_ticket_user_rel', column1='ticket_id', column2='user_id',
        string='Assignees', default=_get_default_user_ids,
        domain=lambda self: [('groups_id', 'in', self.env.ref('rt_helpdesk.rt_helpdesk_group_helpdesk_user').id)],
        tracking=True)
    
    tag_ids = fields.Many2many(
        'rt.helpdesk.ticket.tag', 'rt_helpdesk_ticket_tag_rel', 'ticket_id', 'tag_id', string='Tags',
        help="Classify and analyze your ticket categories like: Problem, Service")    
        
    color = fields.Integer(string='Color Index')
       

    @api.model
    def get_first_stage(self):
        return self.env['rt.helpdesk.ticket.stage'].search([], order='sequence asc', limit=1) 
            
    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        return self.env['rt.helpdesk.ticket.stage'].search([], order=order)
                    
    stage_id = fields.Many2one(
        'rt.helpdesk.ticket.stage', string='Stage', index=True, tracking=True, 
        copy=False, 
        ondelete='restrict',
        group_expand='_read_group_stage_ids',
        #default=get_first_stage,        
        )       

    team_id = fields.Many2one('rt.helpdesk.ticket.team', 
                            string='Team',  
                            ondelete="set null",
                            index=True,tracking=True)


    product_id = fields.Many2one(
        'product.product', string='Product', 
        change_default=True,  ondelete='restrict')

    direction = fields.Selection([
        ('incoming', 'Incoming'),
        ('outgoing', 'Outgoing')
    ], string='Direction',         
        tracking=True,
        copy=False, 
        default='incoming', 
        store=True)

    origin_id = fields.Many2one('rt.helpdesk.ticket.origin', 'Origin', index=True, ondelete='set null')
    
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    
    last_message_on = fields.Datetime(
        string='Last Message On',
        default=fields.Datetime.now,
        copy=False,
    )
      
      
    ticket_is_opt_out_direction_flow_flag = fields.Boolean(default=False,
        copy=False,
        string='Is to change direction flow',
        help="Technical field in order to bypass the direction flow when stage change.")

    date_deadline = fields.Date(string='Deadline', index=True, copy=False, tracking=True)
    
    is_closed = fields.Boolean(related="stage_id.is_closed", string="Closing Stage", readonly=True, related_sudo=False)    
        
    date_end = fields.Datetime(string='Ending Date', index=True, copy=False)
    
    color_html = fields.Char(related="stage_id.color_html", string="Color HTML Stage", readonly=True, related_sudo=False)    
    
    
    # owner
    res_model_id = fields.Many2one(
        'ir.model', 'Document Model',
        index=True, ondelete='cascade')
    res_model = fields.Char(
        'Related Document Model',
        index=True, related='res_model_id.model', precompute=True, compute_sudo=True, store=True, readonly=True)
    res_id = fields.Many2oneReference(string='Related Document ID', index=True, model_field='res_model')
    res_name = fields.Char(
        'Document Name', compute='_compute_res_name', compute_sudo=True, store=True,
        help="Display name of the related document.", readonly=True)
    


    internal_note_html = fields.Html(string='Notes')
     
    def action_open_document(self):
        """ 
        Document related
        Opens the related record based on the model and ID 
        """
        self.ensure_one()
        return {
            'res_id': self.res_id,
            'res_model': self.res_model,
            'target': 'current',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
        }
        

    def test_action_open_document(self):
        """ 
            Testing purpose
        """
        self.ensure_one()
        ticket_email_normalized = tools.email_normalize(self.email_from) or self.email_from or False


    @api.depends('res_model', 'res_id')
    def _compute_res_name(self):
        """
        Document related
        compute document name based on res_model and res_id
        """
        for ticket in self:
            if ticket.res_model and ticket.res_id:
                record = self.env[ticket.res_model].browse(ticket.res_id)
                if record.exists():
                    ticket.res_name = record.display_name
                else:
                    ticket.res_name = False
            else:
                ticket.res_name = False

    # portal.mixin override
    def _compute_access_url(self):
        """
            Defined in portal mixin
            Called from -
                - Portal Tree view.
                
        """
        super(rt_helpdesk_ticket, self)._compute_access_url()
        for ticket in self:
            ticket.access_url = f'/my/rt_helpdesk/tickets/{ticket.id}'                


    @api.onchange('team_id')
    def team_id_change(self):
        """
            When team is changed, we filled assigned as per selected teaam.
        """
        if not self.team_id:
            self.user_ids = [(6, 0, [self.env.uid])]
            #self.user_ids = False
            return
        if self.team_id.member_ids:
            self.user_ids = [(6,0,self.team_id.member_ids.ids)]

            
    # def _phone_get_number_fields(self):   
    #     """ 
    #     Defined in phone_validation app - mail.thread.phone
    #     Use mobile or phone fields to compute sanitized phone number 
    #     """
    #     return ['mobile', 'phone']
            
    def _get_partner_email_update(self):
        """
        Helper method to check whether ticket email_from is 
        same as partner email or not
        """

        self.ensure_one()
        if self.partner_id and self.email_from != self.partner_id.email:
            ticket_email_normalized = tools.email_normalize(self.email_from) or self.email_from or False
            partner_email_normalized = tools.email_normalize(self.partner_id.email) or self.partner_id.email or False
            return ticket_email_normalized != partner_email_normalized
        return False
                
    @api.depends('partner_id.email')
    def _compute_email_from(self):
        """
            Assigned partner email to ticket email_from
        """
        for ticket in self:
            if ticket.partner_id.email and ticket._get_partner_email_update():
                ticket.email_from = ticket.partner_id.email

    def _inverse_email_from(self):
        """
            Assigned ticket email_from to partner email
        """     
        for ticket in self:
            if ticket._get_partner_email_update():
                ticket.partner_id.email = ticket.email_from
             
    def _get_partner_phone_update(self):
        """
        Helper method to check whether ticket phone is 
        same as partner phone or not

        Calculate if we should write the phone on the related partner. When
        the phone of the lead / partner is an empty string, we force it to False
        to not propagate a False on an empty string.

        Done in a separate method so it can be used in both ribbon and inverse
        and compute of phone update methods.
        """
        self.ensure_one()
        if self.partner_id and self.phone != self.partner_id.phone:
            ticket_phone_formatted = self._phone_format(fname='phone') or self.phone or False
            partner_phone_formatted = self.partner_id._phone_format(fname='phone') or self.partner_id.phone or False
            return ticket_phone_formatted != partner_phone_formatted
        return False
                        
    @api.depends('partner_id.phone')
    def _compute_phone(self):
        """
            Assigned partner phone to ticket phone
        """        
        for ticket in self:
            if ticket.partner_id.phone and ticket._get_partner_phone_update():
                ticket.phone = ticket.partner_id.phone

    def _inverse_phone(self):
        """
            Assigned ticket phone to partner phone
        """          
        for ticket in self:
            if ticket._get_partner_phone_update():
                ticket.partner_id.phone = ticket.phone

    def _get_partner_mobile_update(self):
        """
        Helper method to check whether ticket mobile is 
        same as partner mobile or not
        """              
        self.ensure_one()
        if self.partner_id and self.mobile != self.partner_id.mobile:
            ticket_mobile_formatted = self._phone_format(fname='mobile') or self.mobile or False
            partner_mobile_formatted = self.partner_id._phone_format(fname='mobile') or self.partner_id.mobile or False
            return ticket_mobile_formatted != partner_mobile_formatted
        return False


    @api.depends('partner_id.mobile')
    def _compute_mobile(self):
        """ 
        Assigned partner mobile to ticket mobile
        compute the new values when partner_id has changed
        """
        for ticket in self:
            if ticket.partner_id.mobile and ticket._get_partner_mobile_update():
                ticket.mobile = ticket.partner_id.mobile

    def _inverse_mobile(self):
        """ 
        Assigned ticket mobile to partner mobile
        """        
        for ticket in self:
            if ticket._get_partner_mobile_update():
                ticket.partner_id.mobile = ticket.mobile
                                                        
    def update_date_end(self, stage_id):
        """
            When is_closed Stage is written at time we also write
            date_end field in order to record Ending Date
        """
        stage = self.env['rt.helpdesk.ticket.stage'].browse(stage_id)
        if stage.is_closed:
            return {'date_end': fields.Datetime.now()}
        return {'date_end': False}
    
    # ------------------------------------------------------------
    # ORM API
    # ------------------------------------------------------------

    # def name_get(self):
    #     result = []
    #     for ticket in self:
    #         result.append((ticket.id, "%s - %s" % (ticket.ticket_number, ticket.name)))
    #     return result
     
    @api.model
    def default_get(self, fields):
        res = super(rt_helpdesk_ticket, self).default_get(fields)
        # Default stage_id and date_end
        if 'stage_id' not in res:
            stage = self.get_first_stage()
            if stage and stage.id:
                res['stage_id'] = stage.id              
                if stage.is_closed:
                    res['date_end'] = fields.Datetime.now()
                
        # Document related
        # Get res_model_id from res_model
        if not fields or 'res_model_id' in fields and res.get('res_model'):
            res['res_model_id'] = self.env['ir.model']._get(res['res_model']).id
        return res
    
        
    #=== CRUD METHODS ===#
    @api.model_create_multi
    def create(self, vals_list):
        """
            To generate sequence number for each ticket.
        """        
        for vals in vals_list:
            if 'ticket_number' not in vals:
                vals['ticket_number'] = self.env['ir.sequence'].next_by_code('rt_helpdesk.rt.helpdesk.ticket') or _('New')
                vals['display_name'] = vals['ticket_number']                

            if 'email_from' in vals:
                ticket_email_normalized =  vals.get('email_from')
                try:
                    ticket_email_normalized = tools.email_normalize( vals.get('email_from')) or  vals.get('email_from') or False
                except Exception:
                    ticket_email_normalized =  vals.get('email_from')
                    pass                
                vals['email_from'] = ticket_email_normalized

            # stage change: update date_end
            # if 'stage_id' in vals:
            #     vals.update(self.update_date_end(vals['stage_id']))
        return super().create(vals_list)


    def write(self, vals):
        # stage change: update date_end
        if 'stage_id' in vals:
            vals.update(self.update_date_end(vals['stage_id']))
        return super(rt_helpdesk_ticket, self).write(vals)

    # ------------------------------------------------------------
    # Messaging API
    # ------------------------------------------------------------
    def _track_template(self, changes):        
        """
            ticket_is_opt_out_direction_flow_flag change value here 
            based on stage setting in order to use it in further method.
             - def _notify_thread
        """
        res = super(rt_helpdesk_ticket, self)._track_template(changes)
        ticket = self[0]
        if 'stage_id' in changes and ticket.stage_id.mail_template_id:
            if ticket.stage_id.is_opt_out_direction_flow:
                ticket.ticket_is_opt_out_direction_flow_flag = True
            res['stage_id'] = (ticket.stage_id.mail_template_id, {
               # 'auto_delete_message': False,
                #'author_id':SUPERUSER_ID,
                'auto_delete_keep_log': False,
                'subtype_id': self.env['ir.model.data']._xmlid_to_res_id('mail.mt_comment'),
                'email_layout_xmlid': 'mail.mail_notification_light'
            })

        return res

    # v 17 METHOD
    def _notify_get_recipients_groups(self, message, model_description, msg_vals=None):
        """ Add access button to everyone to the 'portal','follower','customer' of the document  """
        groups = super()._notify_get_recipients_groups(
            message, model_description, msg_vals=msg_vals
        )
        if not self:
            return groups

        self.ensure_one()
        local_msg_vals = dict(msg_vals or {})
        # This allows partners added to the email list in the sending wizard to access this document.
        for group_name, _group_method, group_data in groups:
            # THIS IS NECESSARY WHEN SOME ONE MANUALLY ADD FOLLOWER IN THE DOCUMENT 
            # AND SEND EMAIL AT THAT TIME THAT FOLLOWER MUST BE ABLE TO VIEW DOCUMENT.
            # THAT'S WHY WE HAVE GIVEN URL HERE WITH ACCESS TOKEN
            if group_name in ['portal','follower','customer'] and self._portal_ensure_token():
                access_link = self._notify_get_action_link(
                    'view', **local_msg_vals, access_token=self.access_token)
                group_data.update({
                    'has_button_access': True,
                    'button_access': {
                        'url': access_link,
                    },
                })
        return groups  



    def _notify_get_reply_to(self, default=None):
        """ Override to set alias of tickets to their helpdesk team if any. """
        aliases = self.sudo().mapped('team_id').sudo()._notify_get_reply_to(default=default)
        res = {ticket.id: aliases.get(ticket.team_id.id) for ticket in self}
        leftover = self.filtered(lambda rec: not rec.team_id)
        if leftover:
            res.update(super(rt_helpdesk_ticket, leftover)._notify_get_reply_to(default=default))
        return res
        

    def email_split(self, msg):
        email_list = tools.email_split((msg.get('to') or '') + ',' + (msg.get('cc') or ''))
        # check left-part is not already an alias
        aliases = self.mapped('team_id.alias_name')
        return [x for x in email_list if x.split('@')[0] not in aliases]
    
    @api.model
    def message_new(self, msg, custom_values=None):
        """ Overrides mail_thread message_new that is called by the mailgateway
            through message_process.
            This override updates the document according to the email.
        """
        # remove default author when going through the mail gateway. Indeed we
        # do not want to explicitly set user_id to False; however we do not
        # want the gateway user to be responsible if no other responsible is
        # found.
        create_context = dict(self.env.context or {})
        # as we create partner at ticket create/update time we don't want to sent
        # notification to the cusstomer to avoid to thread/email in client inbox.
        # if customer still has issue with notification then we increase the 
        # limit of 50 to  higher to force send email which runing the fetch mail service.
                
        if custom_values is None:
            custom_values = {}
        now = fields.Datetime.now()
        ticket_number = self.env['ir.sequence'].next_by_code('rt_helpdesk.rt.helpdesk.ticket') or _('New')
        
        defaults = {
            'name': msg.get('subject') or _("No Subject"),
            'email_from': msg.get('from'),
            'partner_id': msg.get('author_id',False),
            'direction': 'incoming',
            'last_message_on': now,
            'ticket_number': ticket_number,
            'display_name': ticket_number,
        }
        if msg.get('priority',False) in dict(AVAILABLE_PRIORITIES):
            defaults['priority'] = msg.get('priority')       
        defaults.update(custom_values)
        
        if 'user_ids' not in defaults and 'team_id' in defaults:
            defaults['user_ids'] = [(6,0,self.env['rt.helpdesk.ticket.team'].browse(defaults['team_id']).member_ids.ids)]         

        if 'team_id' in defaults:
            team = self.env['rt.helpdesk.ticket.team'].browse(defaults['team_id'])         
            if 'ticket_type_id' not in defaults and team.default_ticket_type_id:
                defaults['ticket_type_id'] = team.default_ticket_type_id.id        
            if 'tag_ids' not in defaults and team.default_tag_ids:
                defaults['tag_ids'] = [(6,0,team.default_tag_ids.ids)]       
            if 'origin_id' not in defaults and team.default_origin_id:
                defaults['origin_id'] = team.default_origin_id.id          

        # Create Partner
        ticket_partner_id = False
        if not msg.get('author_id',False):
            if msg.get('from',False):
                ticket_partner_id = self.env['res.partner'].find_or_create( msg.get('from')).id                
                defaults['partner_id'] = ticket_partner_id
        # Create Partner            
        defaults.update(custom_values)

        ticket = super(rt_helpdesk_ticket, self.with_context(create_context)).message_new(msg, custom_values=defaults)
        # Portal Access Token
        ticket._portal_ensure_token()
        # Portal Access Token  

        if ticket.email_cc:
            for email in tools.email_split_and_format(ticket.email_cc):        
                self.env['res.partner'].find_or_create(email)                

        email_list = ticket.email_split(msg)
        partner_ids = [p.id for p in self.env['mail.thread']._mail_find_partner_from_emails(email_list, records=ticket, force_create=False) if p]

        if ticket_partner_id and ticket_partner_id not in partner_ids:
            partner_ids.append(ticket_partner_id)

        ticket.message_subscribe(partner_ids)
        return ticket
    
    def message_update(self, msg, update_vals=None):
        """ Override to update the ticket according to the email. """
        #update_context = dict(self.env.context or {})
        # as we create partner at ticket create/update time we don't want to sent
        # notification to the cusstomer to avoid to thread/email in client inbox.
        # if customer still has issue with notification then we increase the 
        # limit of 50 to  higher to force send email which runing the fetch mail service.

        #update_context['mail_notrack'] = True
        #res =  super(rt_helpdesk_ticket, self.with_context(update_context)).message_update(msg, update_vals=update_vals)
        res =  super(rt_helpdesk_ticket, self).message_update(msg, update_vals=update_vals)

        if self.email_cc:
            for email in tools.email_split_and_format(self.email_cc):        
                self.env['res.partner'].find_or_create(email)   
        
        email_list = self.email_split(msg)
        partner_ids = [p.id for p in self.env['mail.thread']._mail_find_partner_from_emails(email_list, records=self, force_create=False) if p]
        self.message_subscribe(partner_ids)
        return res
    
    def _message_get_suggested_recipients(self):  
        """ Returns suggested recipients for ids. Those are a list of
        tuple (partner_id, partner_name, reason, default_create_value), to be managed by Chatter. """
                  
        recipients = super(rt_helpdesk_ticket, self)._message_get_suggested_recipients()
        try:
            for ticket in self:
                if ticket.partner_id and ticket.partner_id.email:
                    ticket._message_add_suggested_recipient(recipients, partner=ticket.partner_id, reason=_('Customer'))
                elif ticket.email_from:
                    ticket._message_add_suggested_recipient(recipients, email=ticket.email_from, reason=_('Customer Email'))
        except AccessError:  # no read access rights -> just ignore suggested recipients because this implies modifying followers
            pass
        return recipients
        
    def _message_post_after_hook(self, message, msg_vals):
        if self.email_from and self.partner_id and not self.partner_id.email:
            self.partner_id.email = self.email_from

        if self.email_from and not self.partner_id:
            # we consider that posting a message with a specified recipient (not a follower, a specific one)
            # on a document without customer means that it was created through the chatter using
            # suggested recipients. This heuristic allows to avoid ugly hacks in JS.
            new_partner = message.partner_ids.filtered(lambda partner: partner.email == self.email_from)
            if new_partner:
                self.search([
                    ('partner_id', '=', False),
                    ('email_from', '=', new_partner.email),
                    #('stage_id.fold', '=', False)
                    ]).write({'partner_id': new_partner.id})
        # use the sanitized body of the email from the message thread to populate the ticket's description
        # if not self.description and message.subtype_id == self._creation_subtype() and self.partner_id == message.author_id:
        #     self.description = message.body
        return super(rt_helpdesk_ticket, self)._message_post_after_hook(message, msg_vals)
        
    def _notify_get_recipients(self, message, msg_vals, **kwargs):
        """
           Do not notify the customer regarding the your ticket created  because they knows
           that they have created a ticket.
        """
        recipients = super()._notify_get_recipients(message, msg_vals, **kwargs)
        context = dict(self.env.context or {})        
        if context.get('fetchmail_cron_running',False):
            return [recipient for recipient in recipients if recipient['type'] not in ['customer', 'portal']]
        return recipients
    # ------------------------------------------------------
    # NOTIFICATION API
    # ------------------------------------------------------
    def _notify_thread(self, message, msg_vals=False, **kwargs):
        """
            Here we perform last_message_on and
            direction flow.
        """        
        recipients_data = super(rt_helpdesk_ticket, self)._notify_thread(message, msg_vals=msg_vals, **kwargs)        

        # For last message on
        now = fields.Datetime.now()
        if message.notification_ids.filtered(lambda notif: notif.notification_type == 'email'):
            self.last_message_on = now
            
        # if direction is opt out then write technical field false and simply return.
            

        if self.ticket_is_opt_out_direction_flow_flag:
            self.ticket_is_opt_out_direction_flow_flag = False
            return recipients_data
        
        # def is_internal_partner(partner):
        #     # Helper to know if the partner is an internal one.
        #     return partner.user_ids and all(user.has_group('base.group_user') for user in partner.user_ids)
        company = self.env.company
        if msg_vals:
            record_company_id = msg_vals.get('record_company_id',False)
            if record_company_id:
                company = self.env['res.company'].sudo().browse(record_company_id)

        def is_internal_partner(partner):
            # Helper to know if the partner is an internal one.
            if company:
                return partner == company.partner_id or (partner.user_ids and all(user._is_internal() for user in partner.user_ids))
            return (partner.user_ids and all(user._is_internal() for user in partner.user_ids))

        #FIX: find complete new way to change direction including email CC
        # If Recipient is not a customer then direction is incoming
        # THINK: Consider here portal message chatter also.  
        # Here we used simple logic to manage incoming and outgoing.

        # if message belong to Discussion subtype for messaging / Chatter and
        # partner author_id is_internal_partner then outgoing else incoming. 
        discussion_subtype_id = self.env['ir.model.data']._xmlid_to_res_id('mail.mt_comment')   
        if message and message.author_id and message.subtype_id and message.subtype_id.id == discussion_subtype_id:
            # if message.is_current_user_or_guest_author:
            #     self.direction = 'incoming'
            # else:
            #     self.direction = 'outgoing'  
            
            if is_internal_partner(message.author_id):
                self.direction = 'outgoing'
            else:
                self.direction = 'incoming'                                          
        return recipients_data


    @api.model
    def get_ticket_dashboard(self, domain = []):
        """
            Get ticket dashboard data used in charts and tile
            to display above the tree and kanban view.
        """
        list_of_stage_id_count_dic = [] 
        list_of_direction_count_dic = []                
        # -----------------------------------------
        # GET TICKET STAGE COUNT
        # -----------------------------------------
        rt_helpdesk_ticket_stage = self.env['rt.helpdesk.ticket.stage'].sudo()
        grouped_res = self.read_group(
            domain = domain,
            fields = ['stage_id'],
            groupby = ['stage_id']
        )
        for group in grouped_res:
            stage_id = group['stage_id']
            if not stage_id:
                list_of_stage_id_count_dic.append({
                    'id': 0,
                    'name': _('Undefined'),
                    'count': group['stage_id_count'],
                    'color_html': '#ffffff',
                    'sequence': 0,
                })
                continue
            stage = rt_helpdesk_ticket_stage.browse(group['stage_id'][0])
            list_of_stage_id_count_dic.append({
                'id': stage.id,
                'name':stage.name,
                'count': group['stage_id_count'],
                'color_html': stage.color_html,
                'sequence': stage.sequence,
            })            
        list_of_stage_id_count_dic = sorted(list_of_stage_id_count_dic, key=lambda s: s['sequence'])
        # -----------------------------------------
        # GET TICKET STAGE COUNT
        # -----------------------------------------
            
        # -----------------------------------------
        # GET TICKET DIRECTION COUNT
        # -----------------------------------------
        grouped_res = self.read_group(
            domain = domain,
            fields = ['direction'],
            groupby = ['direction']
        )
        for group in grouped_res:
            direction = group['direction']
            if not direction:
                list_of_direction_count_dic.append({
                    'name': _('Undefined'),
                    'count': group['direction_count'],
                    'classes': 'bg-dark',
                    'sequence': 0,
                })
                continue
            direction_name = _('Incoming')
            direction_classes = 'bg-danger'
            direction_sequence = 1            
            if direction == 'outgoing':
                direction_name = _('Outgoing')
                direction_classes = 'bg-success'
                direction_sequence = 2                   
            list_of_direction_count_dic.append({
                'name':direction_name,
                'count': group['direction_count'],
                'classes': direction_classes,
                'sequence': direction_sequence,
            })            
        list_of_direction_count_dic = sorted(list_of_direction_count_dic, key=lambda s: s['sequence'])
        # -----------------------------------------
        # GET TICKET DIRECTION COUNT
        # -----------------------------------------                    
        ticket_dashboard = {
            'list_of_stage_id_count_dic':list_of_stage_id_count_dic,
            'list_of_direction_count_dic':list_of_direction_count_dic,
        }
        return ticket_dashboard
    
    
    def ticket_field_widget_format(self):
        """
            Get ticket field widget data
            to display in sale, purchase field widget etc etc.
        """
        fields = ['id','name','ticket_number','product_id','stage_id','user_ids','direction','date_deadline','create_date']
        tickets_data = self.read(fields)
        for ticket, data in zip(self, tickets_data):
            if ticket.stage_id:
                data['stage_id_color_html'] = ticket.stage_id.color_html
            if ticket.user_ids.sudo():    
                data['user_ids_name'] = ', '.join(ticket.user_ids.sudo().mapped('name'))        
        return tickets_data
    