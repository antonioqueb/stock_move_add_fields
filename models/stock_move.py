from odoo import fields, models

class StockMove(models.Model):
    _inherit = 'stock.move'

    gramaje = fields.Float(string="Gramaje")
    ancho = fields.Float(string="Ancho")
    tipo = fields.Char(string="Tipo")
    kilos = fields.Float(string="Kilos")
    planta = fields.Char(string="Planta")

    def _action_done(self, cancel_backorder=False):
        """
        Sobrecargar para evitar que las líneas de movimientos se agrupen
        si tienen diferentes valores en los campos personalizados.
        """
        res = super(StockMove, self)._action_done(cancel_backorder=cancel_backorder)

        for move in self:
            # Evitar la agrupación si las características personalizadas son diferentes
            if move.gramaje or move.ancho or move.tipo or move.kilos or move.planta:
                move._do_not_group_custom_fields()

        return res

    def _do_not_group_custom_fields(self):
        """
        Método para manejar la no agrupación de movimientos
        que tienen diferentes valores en campos personalizados.
        """
        # Puedes implementar la lógica aquí si es necesario.
        pass

    def _merge_moves(self):
        """
        Sobrecargar la lógica de agrupación de movimientos para considerar los campos personalizados.
        """
        grouped_moves = {}
        for move in self:
            # Crear una clave única basada en el producto y los campos personalizados
            key = (move.product_id.id, move.gramaje, move.ancho, move.tipo, move.kilos, move.planta)
            
            # Agrupar solo si ya existe una línea con la misma clave
            if key in grouped_moves:
                grouped_moves[key].quantity_done += move.quantity_done
            else:
                grouped_moves[key] = move

        return list(grouped_moves.values())
