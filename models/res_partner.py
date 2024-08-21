# -*- coding: utf-8 -*-

from odoo import fields, models

class res_partner(models.Model):
    _inherit = 'res.partner'

    rt_helpdesk_ticket_count = fields.Integer("Helpdesk Tickets", compute='_rt_helpdesk_compute_rt_helpdesk_ticket_count')

    # def _rt_helpdesk_compute_rt_helpdesk_ticket_count(self):
    #     # retrieve all children partners and prefetch 'parent_id' on them
    #     all_partners = self.with_context(active_test=False).search_fetch([('id', 'child_of', self.ids)])
    #     all_partners.read(['parent_id'])

    #     ticket_data = self.env['rt.helpdesk.ticket'].read_group(
    #         [('partner_id', 'in', all_partners.ids)],
    #         fields=['partner_id'], groupby=['partner_id'],
    #     )
               
    #     self.rt_helpdesk_ticket_count = 0
    #     for group in ticket_data:
    #         partner = self.browse(group['partner_id'][0])
    #         while partner:
    #             if partner in self:
    #                 partner.rt_helpdesk_ticket_count += group['partner_id_count']
    #             partner = partner.parent_id



    def _rt_helpdesk_compute_rt_helpdesk_ticket_count(self):
        # retrieve all children partners and prefetch 'parent_id' on them
        all_partners = self.with_context(active_test=False).search_fetch(
            [('id', 'child_of', self.ids)], ['parent_id'],
        )

        ticket_data = self.env['rt.helpdesk.ticket'].with_context(active_test=False)._read_group(
            domain=[('partner_id', 'in', all_partners.ids)],
            groupby=['partner_id'], aggregates=['__count']
        )
        self_ids = set(self._ids)

        self.rt_helpdesk_ticket_count = 0
        for partner, count in ticket_data:
            while partner:
                if partner.id in self_ids:
                    partner.rt_helpdesk_ticket_count += count
                partner = partner.parent_id

    def rt_helpdesk_action_open_rt_helpdesk_ticket(self):
        '''
        This function returns an action that displays the tickets from partner.
        '''        
        action = self.env["ir.actions.actions"]._for_xml_id("rt_helpdesk.rt_helpdesk_action_ticket_tree_view")
        action['context'] = {}
        action['domain'] = [('partner_id', 'child_of', self.ids)]
        return action
    

