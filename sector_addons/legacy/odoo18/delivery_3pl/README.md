# delivery_3pl — 3PL Delivery Operations Management

## الوصف (Arabic)

موديول Odoo 18 لإدارة عمليات التوصيل للشركات المزودة لخدمات اللوجستيات التابعة لمنصات توصيل الطعام في السعودية (Keeta, HungerStation, Jahez, Noon Food, Ninja Food, وغيرها).

### الميزات الرئيسية

- **إدارة الشركات والفروع** — هيكل شركة/مدينة/فرع كامل
- **إدارة العقود** — عقود موديولية لكل فرع (شحن حزم، خدمات)
- **إدارة السائقين (Riders)** — مقاولون مستقلون (غير مرتبط بـ hr.employee)
- **محرك التسعير المتقدم** — أسعار لكل طلب / مسافة / شرائح متدرجة / راتب ثابت
- **تتبع الأداء** — يومي وشهري مع مؤشرات ملونة
- **إدارة أهداف الشركة** — مستويات A/B/C/D
- **إدارة الخصومات** — وقود، إيجار، مسكن، سلف، طعام
- **استيراد Excel** — محرك استيراد مع خريطة أعمدة قابلة للتخصيص
- **التسوية والموافقة** — سير عمل متعدد المراحل مع تفصيل الحوافز
- **المحفظة والغرامات** — Wallet & Penalty Management
- **تقارير BI ولوحات بيانات** — لوحات إدارية وتقارير شاملة

---

## Description (English)

An Odoo 18 module for managing third-party logistics (3PL) delivery operations
for food delivery platforms in Saudi Arabia.

### Key Features

| Feature | Details |
|---|---|
| Company & Branch | Multi-city, multi-branch hierarchy |
| Contract Management | Versioned contracts per branch (Parcel/Service types) |
| Rider Management | Independent contractors (separate from `hr.employee`) |
| Pricing Engine | Per-order, per-distance, tiered slabs, fixed salary, experience & capacity incentives |
| Performance Tracking | Daily & monthly with color-coded validity indicators |
| Company Targets | A/B/C/D level target configuration |
| Rider Deductions | Fuel, rent, housing, advance, food |
| Excel Import | Column-mapping engine for bulk data import |
| Settlement Workflow | Multi-stage approval with incentive breakdown |
| Wallet & Penalties | Full wallet and penalty lifecycle management |
| BI / Dashboards | Reports and management dashboards |

---

## Module Information

| Field | Value |
|---|---|
| **Module Name** | `delivery_3pl` |
| **Version** | `18.0.3.0.0` |
| **Odoo Version** | 18.0 |
| **Category** | Operations / Delivery |
| **License** | LGPL-3 |
| **Author** | 3PL Solutions |

---

## Dependencies

### Odoo Modules
- `base`
- `mail`
- `web`
- `hr_contract`

### Python Packages
- `openpyxl` — required for Excel import functionality

---

## Installation

### 1. Copy the module to your Odoo addons path

```bash
cp -r delivery_3pl /path/to/odoo/addons/
# or add odoo-addons/ to your addons_path in odoo.conf
```

### 2. Install Python dependency

```bash
pip install openpyxl
```

### 3. Update `odoo.conf` addons path (if needed)

```ini
[options]
addons_path = /path/to/odoo/addons,/path/to/odoo-addons
```

### 4. Restart Odoo server

```bash
./odoo-bin -c odoo.conf
```

### 5. Install via Odoo UI

1. Go to **Settings → Apps**
2. Click **Update Apps List** (or enable developer mode first)
3. Search for **"3PL Delivery Operations Management"**
4. Click **Install**

---

## Module Structure

```
delivery_3pl/
├── __manifest__.py          # Module metadata and dependencies
├── __init__.py              # Python package init
├── models/                  # Business logic (Python)
│   ├── delivery_city.py     # City management
│   ├── delivery_branch.py   # Branch management
│   ├── delivery_company.py  # Company (3PL partner) management
│   ├── delivery_contract.py # Contract & pricing configuration
│   ├── delivery_rider.py    # Rider (delivery agent) management
│   ├── delivery_pricing.py  # Pricing engine
│   ├── delivery_incentive.py# Incentive rules
│   ├── delivery_performance.py  # Performance tracking
│   ├── delivery_target.py   # Company target management
│   ├── delivery_settlement.py   # Settlement & approval workflow
│   ├── delivery_wallet.py   # Wallet management
│   ├── delivery_penalty.py  # Penalty management
│   ├── delivery_import.py   # Excel import engine
│   ├── delivery_column_map.py   # Column mapping for imports
│   ├── delivery_dashboard.py    # Dashboard data
│   └── delivery_hr_contract.py  # HR contract extension
├── views/                   # XML views & menus
├── security/                # Access rights & record rules
├── data/                    # Master data (XML)
├── report/                  # PDF report templates
├── wizard/                  # Transient models
├── i18n/                    # Translations
└── static/                  # JS / SCSS / XML assets
    └── src/
        ├── js/dashboard.js
        ├── scss/dashboard.scss
        └── xml/dashboard.xml
```

---

## Notes for Developers

- Riders are **not** `hr.employee` records — they use a dedicated `delivery.rider` model.
- The pricing engine supports multiple calculation modes: per-order, per-distance, tiered slabs, and fixed salary — configurable per contract.
- The Excel import engine uses a column-map configuration allowing operators to map any Excel column to the corresponding system field without code changes.
- Settlement workflow has multi-stage approval with full incentive breakdown before final payment.
- The module includes demo data (`data/delivery_demo.xml`) for testing purposes.
