# -*- coding: utf-8 -*-

from odoo import api, fields, models

class Origin(models.Model):
    """ 
    Model for ticket origins. 
    """
    _name = "rt.helpdesk.ticket.origin"
    _description = "Ticket Origin"
    _rec_name = 'name'
    _order = "sequence, name, id"


    name = fields.Char('Origin Name', required=True, translate=True)
    sequence = fields.Integer('Sequence', default=1, help="Used to order origins. Lower is better.")
