# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError
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
        ]
        return fields + custom_fields

    def _action_done(self, cancel_backorder=False):
        for move in self:
            product = move.product_id
            if product.tracking != 'none':
                lines_without_lot = move.move_line_ids.filtered(lambda l: not l.lot_id)
                if lines_without_lot:
                    missing_lots_lines = "\n".join(lines_without_lot.mapped('product_id.display_name'))
                    raise UserError(
                        "No se ha asignado lote a todas las líneas para el producto '%s'. "
                        "Por favor verifica las líneas antes de validar.\n Líneas afectadas:\n%s" % (product.display_name, missing_lots_lines)
                    )

        _logger.info("Iniciando validación (_action_done). Movimientos: %s", self.ids)
        res = super(StockMove, self)._action_done(cancel_backorder=cancel_backorder)
        
        for move in self:
            _logger.info("StockMove %s validado con lotes: %s", move.id, move.move_line_ids.mapped('lot_id.name'))

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
            key = (
                move.product_id.id,
                move.gramaje,
                move.ancho,
                move.tipo,
                move.kilos,
                move.planta,
            )

            if key in moves_by_key:
                existing_move = moves_by_key[key]
                for line in move.move_line_ids:
                    existing_line = existing_move.move_line_ids.filtered(lambda l: (
                        l.product_id == line.product_id and
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
                        # Aquí está la corrección definitiva:
                        new_line = line.copy({
                            'move_id': existing_move.id,
                            # NO ASIGNAR lot_id AQUÍ DIRECTAMENTE.
                        })
                        # Asignamos explícitamente el lot_id después de crear la línea
                        if line.lot_id:
                            new_line.write({'lot_id': line.lot_id.id})

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
