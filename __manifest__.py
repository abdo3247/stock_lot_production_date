{
    'name': 'Stock Lot — Date de production',
    'version': '19.0.1.2.0',
    'category': 'Inventory/Inventory',
    'summary': (
        "Date de production sur stock.lot, utilisée comme base "
        "de calcul des dates d'expiration/alerte/enlèvement/péremption."
    ),
    'author': 'Abdallah',
    'license': 'LGPL-3',
    'depends': ['stock', 'product_expiry'],
    'data': [
        'data/ir_config_parameter.xml',
        'views/stock_lot_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
