# Stock Lot — Date de production (Odoo 19)

Module Odoo 19 qui étend `stock.lot` avec un champ **`production_date`** servant de base de calcul aux 4 dates standard de `product_expiry`.

**Auteur :** Abdallah | **Licence :** LGPL-3 | **Version :** 19.0.1.0.0

---

## Description

Par défaut, Odoo calcule les dates d'expiration d'un lot à partir de sa date de **réception/création**. Ce module remplace cette base par la **date de fabrication** (DoP — Date of Production) du lot.

Le module supporte également un **parsing automatique optionnel** du nom du lot par regex configurable : utile pour les produits importés dont le numéro de lot encode la DoP et/ou la DoE (Date of Expiry).

## Dépendances

- `stock` (Inventaire)
- `product_expiry` (Dates d'expiration — module standard Odoo)

## Installation

```bash
# Copier dans le répertoire des addons custom
cp -r stock_lot_production_date /path/to/odoo/custom-addons/

# Installer (première fois)
odoo-bin -d <db> -i stock_lot_production_date --stop-after-init

# Mettre à jour
odoo-bin -d <db> -u stock_lot_production_date --stop-after-init
```

## Usage

1. **Inventaire → Produits → Lots/N° de série → Nouveau**
2. Saisir la **Date de production**
3. Les 4 dates sont recalculées automatiquement :

| Champ Odoo       | Calcul                                           |
|------------------|--------------------------------------------------|
| `expiration_date`| `production_date` + `expiration_time` jours      |
| `use_date`       | `production_date` + `use_time` jours (DLUO)      |
| `removal_date`   | `production_date` + `removal_time` jours         |
| `alert_date`     | `production_date` + `alert_time` jours           |

> Les durées (`expiration_time`, `use_time`, etc.) sont configurées sur la fiche produit, onglet **Inventaire**.

## Configuration du parser regex

Le parser est **désactivé par défaut** (paramètre vide). Pour l'activer :

**Paramètres techniques → Paramètres système**

| Clé | Description |
|-----|-------------|
| `stock_lot_production_date.lot_name_regex` | Regex avec groupes nommés `dop` et/ou `doe` |
| `stock_lot_production_date.lot_date_format` | Format strptime (défaut : `%y%m%d` = AAMMJJ) |

### Exemples de configuration

| Format de n° de lot         | Regex                                      | Format date |
|-----------------------------|--------------------------------------------|-------------|
| `340KTSQ12-260116-270116`   | `(?P<dop>\d{6})-(?P<doe>\d{6})$`          | `%y%m%d`    |
| `L20260116E20270116`        | `L(?P<dop>\d{8})E(?P<doe>\d{8})`          | `%Y%m%d`    |
| `260116/270116/BATCH42`     | `^(?P<dop>\d{6})/(?P<doe>\d{6})/`         | `%y%m%d`    |

> **Note :** Le paramètre est **par instance** (stocké dans `ir.config_parameter`). Le configurer sur chaque base selon le format des lots du client.

> **Priorité :** Si `production_date` est définie ET que le produit a des durées configurées, les dates calculées depuis `production_date + durée` ont priorité sur les dates éventuellement parsées depuis le nom du lot.

## Tests

```bash
odoo-bin -d <db> --addons-path=...,./custom-addons \
    -i stock_lot_production_date \
    --test-enable --stop-after-init --log-level=test
```

6 cas couverts : calcul des 4 dates, non-écrasement sans DoP, parser désactivé par défaut, parser activé (DoP + DoE), date invalide ignorée, write() sur lot existant.

## Roadmap

- [ ] Wizard de recalcul en masse sur les lots existants
- [ ] Rapport de traçabilité avec date de production
- [ ] Champ `production_date` dans les rapports de livraison/réception
