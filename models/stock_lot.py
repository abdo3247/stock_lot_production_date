import logging
import re
from datetime import datetime, timedelta

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class StockLot(models.Model):
    _inherit = 'stock.lot'

    production_date = fields.Date(
        string='Date de production',
        index=True,
        copy=False,
        help=(
            "Date de fabrication du lot ou numéro de série. "
            "Sert de base de calcul aux dates d'expiration, de péremption (DLUO), "
            "d'enlèvement et d'alerte, en remplacement de la date de réception/création."
        ),
    )

    # ── Paramètres système ────────────────────────────────────────────────────

    def _get_regex_params(self):
        """Renvoie (pattern, date_fmt) depuis ir.config_parameter."""
        get_param = self.env['ir.config_parameter'].sudo().get_param
        pattern = get_param('stock_lot_production_date.lot_name_regex', default='')
        date_fmt = get_param(
            'stock_lot_production_date.lot_date_format', default='%y%m%d'
        )
        return pattern, date_fmt

    # ── Calcul des dates d'expiration ─────────────────────────────────────────

    def _get_expiry_vals_from_production(self):
        """Calcule et renvoie les vals des 4 dates depuis production_date du lot."""
        self.ensure_one()
        if not self.production_date or not self.product_id:
            return {}
        product = self.product_id
        base = datetime.combine(self.production_date, datetime.min.time())
        vals = {}
        if product.expiration_time:
            vals['expiration_date'] = base + timedelta(days=product.expiration_time)
        if product.use_time:
            vals['use_date'] = base + timedelta(days=product.use_time)
        if product.removal_time:
            vals['removal_date'] = base + timedelta(days=product.removal_time)
        if product.alert_time:
            vals['alert_date'] = base + timedelta(days=product.alert_time)
        return vals

    def _compute_expiry_dates_from_production(self):
        """Recalcule et persiste les 4 dates d'expiration à partir de production_date."""
        for lot in self:
            vals = lot._get_expiry_vals_from_production()
            if vals:
                lot.with_context(skip_lot_recompute=True).write(vals)

    # ── Parsing du nom du lot ─────────────────────────────────────────────────

    def _parse_dates_from_name(self):
        """Parse les groupes DoP/DoE depuis lot.name si le regex est configuré."""
        pattern, date_fmt = self._get_regex_params()
        if not pattern:
            return

        try:
            compiled = re.compile(pattern)
        except re.error as exc:
            _logger.warning(
                "stock_lot_production_date: regex invalide %r : %s", pattern, exc
            )
            return

        for lot in self:
            if not lot.name:
                continue
            match = compiled.search(lot.name)
            if not match:
                continue

            groups = match.groupdict()
            vals = {}

            dop_str = groups.get('dop')
            if dop_str:
                try:
                    dop = datetime.strptime(dop_str, date_fmt).date()
                    vals['production_date'] = dop
                except ValueError:
                    _logger.warning(
                        "stock_lot_production_date: impossible de parser DoP %r "
                        "avec le format %r (lot %r).",
                        dop_str, date_fmt, lot.name,
                    )

            doe_str = groups.get('doe')
            if doe_str:
                try:
                    doe = datetime.strptime(doe_str, date_fmt)
                    vals['expiration_date'] = doe
                except ValueError:
                    _logger.warning(
                        "stock_lot_production_date: impossible de parser DoE %r "
                        "avec le format %r (lot %r).",
                        doe_str, date_fmt, lot.name,
                    )

            if vals:
                lot.with_context(skip_lot_recompute=True).write(vals)

    # ── Onchange (UX formulaire) ───────────────────────────────────────────────

    @api.onchange('production_date', 'product_id')
    def _onchange_production_date(self):
        """Met à jour les dates d'expiration à la saisie de la date de production."""
        for lot in self:
            vals = lot._get_expiry_vals_from_production()
            for fname, value in vals.items():
                setattr(lot, fname, value)

    # ── Overrides ORM ─────────────────────────────────────────────────────────

    @api.model_create_multi
    def create(self, vals_list):
        lots = super().create(vals_list)
        lots._parse_dates_from_name()
        lots._compute_expiry_dates_from_production()
        return lots

    def write(self, vals):
        res = super().write(vals)
        if self.env.context.get('skip_lot_recompute'):
            return res
        lots = self.with_context(skip_lot_recompute=True)
        if 'name' in vals:
            lots._parse_dates_from_name()
        if 'production_date' in vals or 'product_id' in vals:
            lots._compute_expiry_dates_from_production()
        return res
