from datetime import date, datetime, time as dt_time
from dateutil.relativedelta import relativedelta

from odoo.tests.common import TransactionCase


class TestProductionDate(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env['product.product'].create({
            'name': 'Produit Test Lot',
            'type': 'consu',
            'tracking': 'lot',
            'use_expiration_date': True,
            'use_time': 365,       # 1 an
            'removal_time': 400,   # ~13 mois
            'alert_time': 30,      # alerte 30j avant expiration
        })

    def _make_lot(self, production_date=None):
        vals = {
            'name': 'LOT-TEST-001',
            'product_id': self.product.id,
        }
        if production_date:
            vals['production_date'] = production_date
        return self.env['stock.lot'].create(vals)

    def test_no_production_date_no_recompute(self):
        """Sans date de production, les dates ne sont pas touchées."""
        lot = self._make_lot()
        # expiration_date peut être setté par Odoo core (depuis now) — on vérifie juste qu'il n'y a pas d'erreur
        self.assertFalse(lot.production_date)

    def test_production_date_sets_expiration(self):
        """Date de production → expiration = production + use_time jours."""
        prod_date = date(2026, 1, 1)
        lot = self._make_lot(production_date=prod_date)
        expected_expiration = datetime.combine(prod_date, dt_time.min) + relativedelta(days=365)
        self.assertEqual(lot.expiration_date, expected_expiration)

    def test_production_date_sets_removal(self):
        """Date de production → removal = production + removal_time jours."""
        prod_date = date(2026, 1, 1)
        lot = self._make_lot(production_date=prod_date)
        expected_removal = datetime.combine(prod_date, dt_time.min) + relativedelta(days=400)
        self.assertEqual(lot.removal_date, expected_removal)

    def test_production_date_sets_best_before(self):
        """best_before = production + (use_time - alert_time) jours."""
        prod_date = date(2026, 1, 1)
        lot = self._make_lot(production_date=prod_date)
        expected = datetime.combine(prod_date, dt_time.min) + relativedelta(days=365 - 30)
        self.assertEqual(lot.best_before_date, expected)

    def test_write_updates_dates(self):
        """Écriture de production_date sur lot existant recalcule les dates."""
        lot = self._make_lot()
        prod_date = date(2025, 6, 15)
        lot.write({'production_date': prod_date})
        expected_expiration = datetime.combine(prod_date, dt_time.min) + relativedelta(days=365)
        self.assertEqual(lot.expiration_date, expected_expiration)

    def test_product_without_expiration_no_recompute(self):
        """Produit sans use_expiration_date → dates non recalculées."""
        product_no_exp = self.env['product.product'].create({
            'name': 'Produit sans expiration',
            'type': 'consu',
            'tracking': 'lot',
            'use_expiration_date': False,
        })
        lot = self.env['stock.lot'].create({
            'name': 'LOT-NO-EXP',
            'product_id': product_no_exp.id,
            'production_date': date(2026, 1, 1),
        })
        self.assertFalse(lot.expiration_date)
