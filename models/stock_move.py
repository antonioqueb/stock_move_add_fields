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
        """
        Incluimos 'move_line_ids.lot_id' para que Odoo evite agrupar
        movimientos con diferentes lotes en sus líneas.
        """
        fields = super()._prepare_merge_move_distinct_fields()
        custom_fields = [
            'gramaje',
            'ancho',
            'tipo',
            'kilos',
            'planta',
            'move_line_ids.lot_id',  # <-- CAMBIO CLAVE
        ]
        return fields + custom_fields

    def _action_done(self, cancel_backorder=False):
        """
        Antes de validar definitivamente, agrupamos las move_line_ids
        por la combinación de producto + campos personalizados. 
        Si alguna línea no tiene lot_id, le asignamos el de otra línea del grupo 
        (si es que hay una que ya lo tenga).
        """
        for move in self:
            lines_by_key = {}
            # Agrupar las líneas por (product_id, gramaje, ancho, tipo, kilos, planta)
            for line in move.move_line_ids:
                key = (
                    line.product_id.id,
                    line.gramaje,
                    line.ancho,
                    line.tipo,
                    line.kilos,
                    line.planta,
                )
                lines_by_key.setdefault(key, []).append(line)

            # Propagar el lot_id a líneas sin lote del mismo grupo
            for key, group_lines in lines_by_key.items():
                # Tomamos la primera línea con lot_id en ese grupo
                lot_id_any = next((l.lot_id for l in group_lines if l.lot_id), False)
                if lot_id_any:
                    for l in group_lines:
                        if not l.lot_id:
                            l.lot_id = lot_id_any

        _logger.info("Iniciando validación de movimientos (_action_done). Movimientos a procesar: %s", self.ids)
        res = super(StockMove, self)._action_done(cancel_backorder=cancel_backorder)

        # Solo a modo de debug adicional
        for move in self:
            _logger.info("StockMove %s con lotes: %s", move.id, move.move_line_ids.mapped('lot_id.name'))
            if move.gramaje or move.ancho or move.tipo or move.kilos or move.planta:
                move._do_not_group_custom_fields()

        return res

    def _do_not_group_custom_fields(self):
        # Método vacío, por si deseas extender la lógica en un futuro
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
            # Añadimos el lote a la clave para no fusionar si difieren en lotes
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

    @api.onchange('lot_name')
    def _onchange_lot_name_set_lot_id(self):
        """
        Si el usuario llena lot_name, se busca o crea un stock.lot con ese nombre.
        Luego se asigna a lot_id, para que al validar no falte la trazabilidad.
        """
        if self.product_id and self.lot_name:
            existing_lot = self.env['stock.lot'].search([
                ('product_id', '=', self.product_id.id),
                ('name', '=', self.lot_name)
            ], limit=1)
            if existing_lot:
                self.lot_id = existing_lot
            else:
                new_lot = self.env['stock.lot'].create({
                    'product_id': self.product_id.id,
                    'name': self.lot_name
                })
                self.lot_id = new_lot
        else:
            self.lot_id = False
