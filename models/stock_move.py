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
        return fields + ['gramaje', 'ancho', 'tipo', 'kilos', 'planta']

    def _merge_moves(self, merge_into=None):
        _logger.info("Iniciando agrupación de movimientos (_merge_moves). merge_into: %s", merge_into.id if merge_into else "None")
        grouped_moves = self.env['stock.move']

        for move in self:
            key = (move.product_id.id, move.gramaje, move.ancho, move.tipo, move.kilos, move.planta)
            _logger.info("Clave generada para movimiento ID %s: %s", move.id, key)

            existing_move = grouped_moves.filtered(lambda m:
                m.product_id.id == move.product_id.id and
                m.gramaje == move.gramaje and
                m.ancho == move.ancho and
                m.tipo == move.tipo and
                m.kilos == move.kilos and
                m.planta == move.planta)

            if existing_move:
                for move_line in move.move_line_ids:
                    existing_line = existing_move.move_line_ids.filtered(lambda l:
                        l.product_id == move_line.product_id and
                        l.lot_id == move_line.lot_id and
                        l.gramaje == move_line.gramaje and
                        l.ancho == move_line.ancho and
                        l.tipo == move_line.tipo and
                        l.kilos == move_line.kilos and
                        l.planta == move_line.planta)

                    if existing_line:
                        existing_line.qty_done += move_line.qty_done
                    else:
                        move_line.copy(default={'move_id': existing_move.id})
            else:
                grouped_moves |= move

        return grouped_moves

    def _action_done(self, cancel_backorder=False):
        _logger.info("Iniciando validación de movimientos (_action_done). Movimientos a procesar: %s", self.ids)
        res = super(StockMove, self)._action_done(cancel_backorder=cancel_backorder)

        for move in self:
            if move.gramaje or move.ancho or move.tipo or move.kilos or move.planta:
                move._do_not_group_custom_fields()

        return res

    def _do_not_group_custom_fields(self):
        # Si no necesitas más funcionalidad específica, puedes eliminar este método por completo.
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


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    gramaje = fields.Float(string="Gramaje")
    ancho = fields.Float(string="Ancho")
    tipo = fields.Char(string="Tipo")
    kilos = fields.Float(string="Kilos")
    planta = fields.Char(string="Planta")