from odoo import fields, models

class StockMove(models.Model):
    _inherit = 'stock.move'

    gramaje = fields.Char(string="Gramaje")
    ancho = fields.Float(string="Ancho")
    tipo = fields.Char(string="Tipo")
    kilos = fields.Float(string="Kilos")
    planta = fields.Char(string="Planta")


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def action_open_label_type(self):
        # Llama al reporte usando el ID correcto registrado en XML
        return self.env.ref('stock_move_add_fields.custom_stock_label_report').report_action(self)
