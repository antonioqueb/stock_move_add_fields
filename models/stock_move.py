from odoo import fields, models
import logging

_logger = logging.getLogger(__name__)

class StockMove(models.Model):
    _inherit = 'stock.move'

    gramaje = fields.Float(string="Gramaje")
    ancho = fields.Float(string="Ancho")
    tipo = fields.Char(string="Tipo")
    kilos = fields.Float(string="Kilos")
    planta = fields.Char(string="Planta")

    def _prepare_merge_move_distinct_fields(self):
        fields = super()._prepare_merge_move_distinct_fields()
        custom_fields = ['gramaje', 'ancho', 'tipo', 'kilos', 'planta']
        return fields + custom_fields

    def _action_done(self, cancel_backorder=False):
        _logger.info("Iniciando validación de movimientos (_action_done). Movimientos a procesar: %s", self.ids)
        
        for move in self:
            for line in move.move_line_ids:
                _logger.info("Mov: %s - Prod: %s - Lote: %s - Cantidad: %s", 
                             move.id, move.product_id.display_name, 
                             line.lot_id.name if line.lot_id else "SIN LOTE", 
                             line.quantity_done)

                if move.product_id.tracking in ['lot', 'serial'] and not line.lot_id:
                    _logger.warning("FALTA LOTE para el producto: %s", move.product_id.display_name)
        
        res = super(StockMove, self)._action_done(cancel_backorder=cancel_backorder)
        
        for move in self:
            if move.gramaje or move.ancho or move.tipo or move.kilos or move.planta:
                move._do_not_group_custom_fields()

        return res

    def _do_not_group_custom_fields(self):
        pass

    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        vals = super()._prepare_move_line_vals(quantity, reserved_quant)
        vals.update({
            'gramaje': self.gramaje,
            'ancho': self.ancho,
            'tipo': self.tipo,
            'kilos': self.kilos,
            'planta': self.planta,
        })
        return vals

    def _merge_moves(self, merge_into=False):
        _logger.info("Iniciando agrupación de movimientos (_merge_moves). merge_into: %s", merge_into)

        moves_by_key = {}
        grouped_moves = self.env['stock.move']

        for move in self:
            key = (move.product_id.id, move.gramaje, move.ancho, move.tipo, move.kilos, move.planta)

            if key in moves_by_key:
                existing_move = moves_by_key[key]
                for line in move.move_line_ids:
                    existing_line = existing_move.move_line_ids.filtered(lambda l: l.product_id == move.product_id and l.lot_id == line.lot_id and
                                                                          l.gramaje == line.gramaje and l.ancho == line.ancho and l.tipo == line.tipo and
                                                                          l.kilos == line.kilos and l.planta == line.planta)
                    if existing_line:
                        existing_line.quantity_done += line.quantity_done
                    else:
                        new_line = line.copy({'move_id': existing_move.id, 'lot_id': line.lot_id.id if line.lot_id else False})
                        _logger.info("Copiando línea de stock con lote: %s", line.lot_id.name if line.lot_id else "SIN LOTE")

                move.state = 'cancel'

            else:
                moves_by_key[key] = move
                grouped_moves |= move

        _logger.info("Finalizando agrupación de movimientos. Movimientos agrupados resultantes: %s", grouped_moves.ids)
        return grouped_moves


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    gramaje = fields.Float(string="Gramaje")
    ancho = fields.Float(string="Ancho")
    tipo = fields.Char(string="Tipo")
    kilos = fields.Float(string="Kilos")
    planta = fields.Char(string="Planta")