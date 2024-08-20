from odoo import fields, models

class StockMove(models.Model):
    _inherit = 'stock.move'

    gramaje = fields.Char(string="Gramaje")
