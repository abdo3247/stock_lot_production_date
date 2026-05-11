# Stock Lot Production Date — Odoo 19

**Auteur :** More ERP | **Site :** https://more-erp.com | **Licence :** LGPL-3

## Fonctionnalités

- Champ **Date de production** sur les lots / numéros de série (`stock.lot`)
- **Recalcul automatique** des dates d'expiration (expiration, DLUO, retrait, alerte) à partir de la date de production + durées configurées sur le produit (`use_time`, `removal_time`, `alert_time`)
- Colonne **Date de production** optionnelle dans la liste des lots
- Colonne **Date de production** optionnelle dans les opérations détaillées des transferts
- Traductions **Français** et **Arabe** incluses

## Prérequis

- Odoo 19.0
- Module `stock` (Inventaire)
- Activer **Dates d'expiration** sur les produits concernés (`use_expiration_date = True`)

## Installation

```bash
# Copier le module dans le répertoire addons
cp -r stock_lot_production_date /path/to/odoo/addons/

# Mettre à jour la liste des modules
./odoo-bin -u stock_lot_production_date -d <base>
```

## Utilisation

1. Ouvrir **Inventaire > Produits > Lots/Numéros de série**
2. Sur la fiche d'un lot, renseigner la **Date de production**
3. Si le produit a les dates d'expiration activées → les dates (`expiration_date`, `removal_date`, etc.) sont recalculées automatiquement

## Logique de calcul

| Champ Odoo          | Calcul                                      |
|---------------------|---------------------------------------------|
| `expiration_date`   | `production_date` + `use_time` jours        |
| `removal_date`      | `production_date` + `removal_time` jours    |
| `best_before_date`  | `production_date` + (`use_time` - `alert_time`) jours |
| `alert_date`        | `production_date` + (`use_time` - `alert_time`) jours |
