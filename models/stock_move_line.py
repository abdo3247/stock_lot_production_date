from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    lot_production_date = fields.Date(
        related='lot_id.production_date',
        string='Date de production',
        store=False,
    )
