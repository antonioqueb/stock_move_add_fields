from odoo import api, fields, models
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
        res = super()._action_done(cancel_backorder=cancel_backorder)
        for move in self:
            # Solo para debug: ¿qué lotes se asignaron a cada move?
            _logger.info("StockMove %s con lotes: %s", move.id, move.move_line_ids.mapped('lot_id.name'))
            if move.gramaje or move.ancho or move.tipo or move.kilos or move.planta:
                move._do_not_group_custom_fields()
        return res

    def _do_not_group_custom_fields(self):
        # Método vacío, por si deseas extender la lógica
        pass

    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        vals = super()._prepare_move_line_vals(quantity, reserved_quant)
        # Copiamos los campos custom al move line
        vals.update({
            'gramaje': self.gramaje,
            'ancho': self.ancho,
            'tipo': self.tipo,
            'kilos': self.kilos,
            'planta': self.planta,
        })
        # NO se asigna lot_id automáticamente, 
        # se usará el onchange en StockMoveLine para crearlo/ligarlo desde lot_name
        return vals

    def _merge_moves(self, merge_into=False):
        _logger.info("Iniciando agrupación de movimientos (_merge_moves). merge_into: %s", merge_into)

        moves_by_key = {}
        grouped_moves = self.env['stock.move']

        for move in self:
            # Añadimos lote en la clave para evitar agrupar si difiere
            lot_id = move.move_line_ids[:1].lot_id.id if move.move_line_ids else False

            key = (
                move.product_id.id,
                move.gramaje,
                move.ancho,
                move.tipo,
                move.kilos,
                move.planta,
                lot_id
            )

            if key in moves_by_key:
                existing_move = moves_by_key[key]
                for line in move.move_line_ids:
                    existing_line = existing_move.move_line_ids.filtered(lambda l: (
                        l.product_id == move.product_id and
                        l.lot_id == line.lot_id and
                        l.gramaje == line.gramaje and
                        l.ancho == line.ancho and
                        l.tipo == line.tipo and
                        l.kilos == line.kilos and
                        l.planta == line.planta
                    ))
                    if existing_line:
                        existing_line.qty_done += line.qty_done
                    else:
                        new_line = line.copy({'move_id': existing_move.id})
                        if line.lot_id:
                            new_line.lot_id = line.lot_id
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

    # Campo lot_name viene de Odoo (para productos con tracking="lot" o "serial").
    # Implementamos un onchange para forzar la creación/búsqueda de un stock.lot
    @api.onchange('lot_name')
    def _onchange_lot_name_set_lot_id(self):
        """
        Si el usuario llena lot_name, se busca o crea un stock.lot con ese nombre.
        Luego se asigna a lot_id, para que al validar no falte la trazabilidad.
        """
        if self.product_id and self.lot_name:
            # Verificamos si ya existe un lote para ese producto con el nombre dado
            existing_lot = self.env['stock.lot'].search([
                ('product_id', '=', self.product_id.id),
                ('name', '=', self.lot_name)
            ], limit=1)
            if existing_lot:
                self.lot_id = existing_lot
            else:
                # Creamos un nuevo lote con el nombre tecleado
                new_lot = self.env['stock.lot'].create({
                    'product_id': self.product_id.id,
                    'name': self.lot_name
                })
                self.lot_id = new_lot
        else:
            # Si lot_name está vacío, dejamos lot_id en blanco
            self.lot_id = False
