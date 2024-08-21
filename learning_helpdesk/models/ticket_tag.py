# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from random import randint

from odoo import fields, models,api,_
from odoo.exceptions import UserError, ValidationError

class Tag(models.Model):
    _name = "rt.helpdesk.ticket.tag"
    _description = "Ticket Tags"
    _rec_name = 'name'
    _order = "sequence, name, id"


    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char('Tag Name', required=True, translate=True)
    sequence = fields.Integer('Sequence', default=1, help="Used to order tags. Lower is better.")    
    color = fields.Integer('Color', default=_get_default_color)


    @api.constrains('name')
    def _check_name_constraint(self):
        """ name must be unique """
        for tag in self.filtered(lambda t: t.name):
            domain = [('id', '!=', tag.id), ('name', '=', tag.name)]
            if self.search(domain):
                raise ValidationError(_('Tag name already exists !'))
            

