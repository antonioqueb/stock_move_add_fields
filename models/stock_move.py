from odoo import fields, models

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    gramaje = fields.Float(string="Gramaje")
    ancho = fields.Float(string="Ancho")
    tipo = fields.Char(string="Tipo")
    kilos = fields.Float(string="Kilos")
    planta = fields.Char(string="Planta")
