{
    'name': 'Date de production dans Lot',
    'version': '19.0.1.0.0',
    'category': 'Inventory/Inventory',
    'summary': 'Ajoute la date de production sur les lots/numéros de série et recalcule les dates d\'expiration',
    'description': """
Module Odoo 19 — Date de production dans les lots de stock.

Fonctionnalités :
- Champ "Date de production" sur les lots / numéros de série (stock.lot)
- Recalcul automatique des dates d'expiration (expiration, DLUO, retrait, alerte)
  à partir de la date de production + durées produit (use_time, removal_time, alert_time)
- Visible dans le formulaire du lot et dans les lignes détaillées des transferts
- Traductions FR et AR incluses
""",
    'author': 'More ERP',
    'website': 'https://more-erp.com',
    'maintainer': 'More ERP',
    'license': 'LGPL-3',
    'depends': [
        'stock',
    ],
    'data': [
        'views/stock_lot_views.xml',
        'views/stock_picking_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
