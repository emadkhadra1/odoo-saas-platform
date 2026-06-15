# تشغيل قطاعات Qimam Solutions Cloud

القطاعات المعتمدة حاليا:

- المقاولات: `CONSTRUCTION_BUSINESS` و template باسم `tenant_template_construction`
- الاستثمار العقاري / ريل ستيت: `REAL_ESTATE_BUSINESS` و template باسم `tenant_template_realestate`
- الموارد البشرية السعودية: `SAUDI_HR_BUSINESS` و template باسم `tenant_template_saudi_hr`
- 3PL واللوجستيات: `THREE_PL_BUSINESS` و template باسم `tenant_template_3pl`

لا نرفع المنصة التعليمية في هذه المرحلة.

## مكان الموديولات على السيرفر

أنشئ مسارات منفصلة للموديولات التجارية:

```bash
mkdir -p /opt/odoo/sector-addons/construction
mkdir -p /opt/odoo/sector-addons/realestate
mkdir -p /opt/odoo/sector-addons/saudi_hr
mkdir -p /opt/odoo/sector-addons/3pl
```

ثم ارفع الموديولات إلى هذه المسارات:

- موديولات المقاولات إلى `/opt/odoo/sector-addons/construction`
- موديولات العقار إلى `/opt/odoo/sector-addons/realestate`
- موديولات HR إلى `/opt/odoo/sector-addons/saudi_hr`
- موديول `delivery_3pl` إلى `/opt/odoo/sector-addons/3pl`

## ربط المسارات مع Docker

إذا كنت تشغل Odoo بأمر `docker run`، أوقف container الحالي وأعد تشغيله مع volumes إضافية:

```bash
docker stop odoo19
docker rm odoo19
docker run -d --name odoo19 \
  --link odoo19-db:db \
  -p 8069:8069 \
  -v /opt/odoo/custom-addons/odoo-saas-platform:/mnt/extra-addons \
  -v /opt/odoo/sector-addons/construction:/mnt/sector-addons/construction \
  -v /opt/odoo/sector-addons/realestate:/mnt/sector-addons/realestate \
  -v /opt/odoo/sector-addons/saudi_hr:/mnt/sector-addons/saudi_hr \
  -v /opt/odoo/sector-addons/3pl:/mnt/sector-addons/3pl \
  odoo:19.0 \
  --addons-path=/usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons,/mnt/sector-addons/construction,/mnt/sector-addons/realestate,/mnt/sector-addons/saudi_hr,/mnt/sector-addons/3pl
```

إذا عندك `docker-compose.yml`، أضف نفس volumes ونفس `--addons-path`.

## تحديث Odoo

```bash
docker restart odoo19
```

ثم من Odoo:

1. Apps
2. Update Apps List
3. ابحث عن موديولات القطاع وتأكد أنها ظاهرة

## إنشاء قواعد Template

لكل قطاع، أنشئ قاعدة template مرة واحدة، ثبت فيها موديولات القطاع، واضبط بيانات الديمو الأساسية:

```text
tenant_template_construction
tenant_template_realestate
tenant_template_saudi_hr
tenant_template_3pl
```

هذه القواعد لا يدخل عليها العملاء مباشرة. هي مصدر النسخ فقط عند اشتراك عميل جديد.

## ربط الخطط بالـ Templates

داخل Odoo:

`SaaS Manager > Configuration > Plans`

اضبط حقل `Template Database`:

- Construction Business -> `tenant_template_construction`
- Real Estate Business -> `tenant_template_realestate`
- Saudi HR Business -> `tenant_template_saudi_hr`
- 3PL Business -> `tenant_template_3pl`

بعدها عندما تنشئ Tenant جديد وتضغط Provision، سيأخذ نسخة من template الخطة المختارة.
