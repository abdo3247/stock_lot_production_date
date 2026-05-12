from odoo import fields, models


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    lot_production_date = fields.Date(
        related='lot_id.production_date',
        string='Date de production',
        store=False,
    )
