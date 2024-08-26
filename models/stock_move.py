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
        pass

    def _merge_moves(self, merge_into=None):
        """
        Sobrecargar la lógica de agrupación de movimientos para considerar los campos personalizados.
        Ahora también acepta el argumento `merge_into`.
        """
        grouped_moves = self.env['stock.move']  # Inicializamos un recordset vacío de stock.move

        for move in self:
            # Crear una clave única basada en el producto y los campos personalizados
            key = (move.product_id.id, move.gramaje, move.ancho, move.tipo, move.kilos, move.planta)

            if merge_into:
                # Fusionar líneas de movimiento en la misma operación, actualizando las cantidades
                for move_line in move.move_line_ids:
                    merge_into_line = merge_into.move_line_ids.filtered(lambda l: l.product_id == move_line.product_id and
                                                                         l.lot_id == move_line.lot_id)
                    if merge_into_line:
                        merge_into_line.qty_done += move_line.qty_done
                    else:
                        # Si no hay línea coincidente, copiarla al movimiento merge_into
                        move_line.copy(default={'move_id': merge_into.id})
            else:
                # Agrupar solo si ya existe un movimiento con la misma clave
                existing_move = grouped_moves.filtered(lambda m: m.product_id.id == move.product_id.id and
                                                               m.gramaje == move.gramaje and
                                                               m.ancho == move.ancho and
                                                               m.tipo == move.tipo and
                                                               m.kilos == move.kilos and
                                                               m.planta == move.planta)
                if existing_move:
                    for move_line in move.move_line_ids:
                        existing_line = existing_move.move_line_ids.filtered(lambda l: l.product_id == move_line.product_id and
                                                                             l.lot_id == move_line.lot_id)
                        if existing_line:
                            existing_line.qty_done += move_line.qty_done
                        else:
                            # Copiar la línea al movimiento existente
                            move_line.copy(default={'move_id': existing_move.id})
                else:
                    grouped_moves += move

        return grouped_moves  # Devolvemos el recordset en lugar de una lista


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    gramaje = fields.Float(string="Gramaje")
    ancho = fields.Float(string="Ancho")
    tipo = fields.Char(string="Tipo")
    kilos = fields.Float(string="Kilos")
    planta = fields.Char(string="Planta")
