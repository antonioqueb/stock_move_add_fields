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

    def _action_done(self, cancel_backorder=False):
        _logger.info("Iniciando validación de movimientos (_action_done). Movimientos a procesar: %s", self.ids)
        try:
            res = super(StockMove, self)._action_done(cancel_backorder=cancel_backorder)
        except Exception as e:
            _logger.exception("Error durante super(_action_done): %s", e)
            raise e

        for move in self:
            _logger.info("Verificando campos personalizados del movimiento (ID: %s). Gramaje: %s, Ancho: %s, Tipo: %s, Kilos: %s, Planta: %s",
                         move.id, move.gramaje, move.ancho, move.tipo, move.kilos, move.planta)

            if move.gramaje or move.ancho or move.tipo or move.kilos or move.planta:
                _logger.info("Llamando a método _do_not_group_custom_fields para movimiento ID: %s", move.id)
                move._do_not_group_custom_fields()
            else:
                _logger.info("Movimiento ID: %s no tiene campos personalizados, omitiendo método _do_not_group_custom_fields.", move.id)

        _logger.info("Finalizando validación de movimientos (_action_done).")
        return res

    def _do_not_group_custom_fields(self):
        _logger.info("Ejecutado _do_not_group_custom_fields para movimiento ID: %s", self.id)
        # De momento no tiene implementación, aquí podrías poner código adicional si necesario.
        pass

    def _merge_moves(self, merge_into=None):
        _logger.info("Iniciando agrupación de movimientos (_merge_moves). merge_into: %s", merge_into.id if merge_into else "None")
        grouped_moves = self.env['stock.move']

        for move in self:
            key = (move.product_id.id, move.gramaje, move.ancho, move.tipo, move.kilos, move.planta)
            _logger.info("Clave generada para movimiento ID %s: %s", move.id, key)

            if merge_into:
                for move_line in move.move_line_ids:
                    merge_into_line = merge_into.move_line_ids.filtered(lambda l:
                        l.product_id == move_line.product_id and
                        l.lot_id == move_line.lot_id and
                        l.gramaje == move_line.gramaje and
                        l.ancho == move_line.ancho and
                        l.tipo == move_line.tipo and
                        l.kilos == move_line.kilos and
                        l.planta == move_line.planta)

                    if merge_into_line:
                        _logger.info("Agrupando línea existente (ID: %s) qty_done antes: %s + %s", 
                                     merge_into_line.id, merge_into_line.qty_done, move_line.qty_done)
                        merge_into_line.qty_done += move_line.qty_done
                    else:
                        _logger.info("Copiando línea (ID original: %s) al movimiento merge_into ID: %s", move_line.id, merge_into.id)
                        move_line.copy(default={'move_id': merge_into.id})
            else:
                existing_move = grouped_moves.filtered(lambda m:
                    m.product_id.id == move.product_id.id and
                    m.gramaje == move.gramaje and
                    m.ancho == move.ancho and
                    m.tipo == move.tipo and
                    m.kilos == move.kilos and
                    m.planta == move.planta)

                if existing_move:
                    _logger.info("Movimiento existente encontrado para agrupación: ID %s", existing_move.id)
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
                            _logger.info("Agrupando línea existente (ID: %s) qty_done antes: %s + %s", 
                                         existing_line.id, existing_line.qty_done, move_line.qty_done)
                            existing_line.qty_done += move_line.qty_done
                        else:
                            _logger.info("Copiando línea (ID original: %s) al movimiento existente ID: %s", move_line.id, existing_move.id)
                            move_line.copy(default={'move_id': existing_move.id})
                else:
                    _logger.info("Agregando nuevo movimiento a agrupación: ID %s", move.id)
                    grouped_moves += move

        _logger.info("Finalizando agrupación de movimientos. Movimientos agrupados resultantes: %s", grouped_moves.ids)
        return grouped_moves

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    gramaje = fields.Float(string="Gramaje")
    ancho = fields.Float(string="Ancho")
    tipo = fields.Char(string="Tipo")
    kilos = fields.Float(string="Kilos")
    planta = fields.Char(string="Planta")
