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
