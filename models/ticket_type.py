# -*- coding: utf-8 -*-

from odoo import api, fields, models

class Type(models.Model):
    """ 
    Model for ticket types. 
    """
    _name = "rt.helpdesk.ticket.type"
    _description = "Ticket Type"
    _rec_name = 'name'
    _order = "sequence, name, id"


    name = fields.Char('Ticket Type Name', required=True, translate=True)
    sequence = fields.Integer('Sequence', default=1, help="Used to order types. Lower is better.")
