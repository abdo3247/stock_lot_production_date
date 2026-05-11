from datetime import datetime, time as dt_time
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class StockLot(models.Model):
    _inherit = 'stock.lot'

    production_date = fields.Date(
        string='Date de production',
        help=(
            "Date de fabrication du lot / numéro de série. "
            "Si le produit utilise les dates d'expiration, les dates sont "
            "recalculées automatiquement à partir de cette date."
        ),
    )

    # ── onchange ─────────────────────────────────────────────────────────────

    @api.onchange('production_date')
    def _onchange_production_date(self):
        for lot in self:
            if lot.production_date and lot.product_id.use_expiration_date:
                lot._recompute_dates_from_production()

    # ── helpers ───────────────────────────────────────────────────────────────

    def _recompute_dates_from_production(self):
        """Recalcule expiration/DLUO/retrait/alerte depuis production_date."""
        self.ensure_one()
        product = self.product_id
        if not self.production_date or not product.use_expiration_date:
            return
        base = datetime.combine(self.production_date, dt_time.min)
        use_days = product.use_time or 0
        removal_days = product.removal_time or 0
        alert_days = product.alert_time or 0
        self.expiration_date = base + relativedelta(days=use_days)
        self.removal_date = base + relativedelta(days=removal_days)
        # best_before = expiration - alert_time
        self.best_before_date = base + relativedelta(days=max(use_days - alert_days, 0))
        self.alert_date = base + relativedelta(days=max(use_days - alert_days, 0))

    # ── ORM overrides ─────────────────────────────────────────────────────────

    @api.model_create_multi
    def create(self, vals_list):
        lots = super().create(vals_list)
        for lot in lots:
            if lot.production_date and lot.product_id.use_expiration_date:
                lot._recompute_dates_from_production()
        return lots

    def write(self, vals):
        res = super().write(vals)
        if 'production_date' in vals:
            for lot in self:
                if lot.production_date and lot.product_id.use_expiration_date:
                    lot._recompute_dates_from_production()
        return res
