from datetime import date, datetime, timedelta

from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestProductionDate(TransactionCase):
    """Tests fonctionnels du champ production_date sur stock.lot."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env['product.product'].create({
            'name': 'Produit Test Expiry',
            'type': 'consu',
            'tracking': 'lot',
            'use_expiration_date': True,
            'expiration_time': 365,   # 1 an
            'use_time': 300,          # 10 mois
            'removal_time': 350,      # ~11,5 mois
            'alert_time': 30,         # 30 jours avant expiration
        })

    def _create_lot(self, name='LOT-TEST', product=None, **extra):
        product = product or self.product
        vals = {'name': name, 'product_id': product.id, **extra}
        return self.env['stock.lot'].create(vals)

    # ── Test 1 : production_date → 4 dates recalculées ────────────────────────

    def test_onchange_computes_expiry(self):
        """Création avec production_date → les 4 dates sont calculées correctement."""
        prod_date = date(2026, 1, 15)
        lot = self._create_lot(production_date=prod_date)

        base = datetime(2026, 1, 15, 0, 0, 0)
        self.assertEqual(lot.expiration_date, base + timedelta(days=365))
        self.assertEqual(lot.use_date, base + timedelta(days=300))
        self.assertEqual(lot.removal_date, base + timedelta(days=350))
        self.assertEqual(lot.alert_date, base + timedelta(days=30))

    # ── Test 2 : sans production_date → dates standard non écrasées ───────────

    def test_no_production_date_no_change(self):
        """Sans production_date, le module ne modifie pas les dates existantes."""
        lot = self._create_lot('LOT-NO-PROD')
        # On fixe manuellement une date d'expiration (simulant ce que product_expiry
        # ferait à la réception) et on vérifie qu'un write sans production_date ne la touche pas.
        sentinel = datetime(2028, 6, 1, 0, 0, 0)
        lot.with_context(skip_lot_recompute=True).write({'expiration_date': sentinel})
        lot.write({'ref': 'REF-001'})  # write sans production_date ni product_id
        self.assertEqual(lot.expiration_date, sentinel)

    # ── Test 3 : parser désactivé par défaut ─────────────────────────────────

    def test_name_parser_disabled_by_default(self):
        """Sans regex configuré, le nom du lot n'est pas parsé."""
        # S'assurer que le paramètre est vide (état initial après installation)
        self.env['ir.config_parameter'].sudo().set_param(
            'stock_lot_production_date.lot_name_regex', ''
        )
        lot = self._create_lot('ABC-260116-270116')
        self.assertFalse(lot.production_date)

    # ── Test 4 : parser activé → DoP et DoE extraits ─────────────────────────

    def test_name_parser_enabled(self):
        """Avec regex configuré, DoP et DoE sont extraits du nom du lot."""
        self.env['ir.config_parameter'].sudo().set_param(
            'stock_lot_production_date.lot_name_regex',
            r'(?P<dop>\d{6})-(?P<doe>\d{6})',
        )
        self.env['ir.config_parameter'].sudo().set_param(
            'stock_lot_production_date.lot_date_format', '%y%m%d'
        )
        lot = self._create_lot('ABC-260116-270116')
        self.assertEqual(lot.production_date, date(2026, 1, 16))
        self.assertEqual(lot.expiration_date, datetime(2027, 1, 16, 0, 0, 0))

    # ── Test 5 (bonus) : date invalide dans le nom → ignorée silencieusement ─

    def test_invalid_date_in_name_is_ignored(self):
        """Une date non parsable dans le nom du lot est ignorée sans lever d'exception."""
        self.env['ir.config_parameter'].sudo().set_param(
            'stock_lot_production_date.lot_name_regex',
            r'(?P<dop>\d{6})-(?P<doe>\d{6})',
        )
        self.env['ir.config_parameter'].sudo().set_param(
            'stock_lot_production_date.lot_date_format', '%y%m%d'
        )
        # Mois 13 → ValueError → warning loggé, pas d'exception
        lot = self._create_lot('ABC-991399-991399')
        self.assertFalse(lot.production_date)
        self.assertFalse(lot.expiration_date)

    # ── Test complémentaire : write('production_date') re-déclenche le calcul ─

    def test_write_production_date_recomputes(self):
        """Écrire production_date sur un lot existant recalcule les dates."""
        lot = self._create_lot('LOT-WRITE')
        self.assertFalse(lot.production_date)
        prod_date = date(2025, 6, 15)
        lot.write({'production_date': prod_date})
        base = datetime(2025, 6, 15, 0, 0, 0)
        self.assertEqual(lot.expiration_date, base + timedelta(days=365))
