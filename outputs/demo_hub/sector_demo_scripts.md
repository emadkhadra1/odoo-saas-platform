# Sector Demo Scripts

استخدم هذه السكربتات في العروض للعميل. كل ديمو يستهدف 7 إلى 10 دقائق.

## 1. 3PL / Delivery Demo

Opening:

> هذه قاعدة مستقلة لشركة لوجستيات تعمل بنظام SaaS، مربوطة بخطة 3PL Business.

Demo flow:

1. افتح Dashboard الأداء.
2. اعرض شركات التوصيل أو service providers.
3. افتح Riders واعرض بيانات مندوب.
4. افتح Contracts وPricing tiers.
5. نفذ أو اعرض Import للعمليات.
6. افتح Settlements واعرض تسوية مندوب أو شركة.
7. اختم بتقرير الأداء والمدفوعات.

Key modules:

```text
delivery_3pl
fleet
hr_contract
hr_payroll
```

Sales angle:

> العميل لا يشتري Odoo عام، بل يشتري دورة تشغيل توصيل كاملة جاهزة كاشتراك.

## 2. Construction Demo

Opening:

> هذه قاعدة مستقلة لشركة مقاولات فيها مشاريع، BOQ، مستخلصات، ميزانيات، وتقارير.

Demo flow:

1. افتح مشروع مقاولات.
2. اعرض BOQ main/sub items.
3. اعرض مقاولي الباطن أو constructors.
4. افتح Progress Bill.
5. اعرض owner progress أو مستخلص المالك.
6. افتح Budgeting.
7. اختم بتقرير project/construction report.

Key modules:

```text
construction_project
b2b_constructors
construction_budgeting
construction_project_reports
financial_custody
```

Sales angle:

> النظام يغطي التشغيل المالي والفني للمشروع، وليس مجرد project tasks.

## 3. Real Estate Demo

Opening:

> هذه قاعدة مستقلة لشركة عقارية تبدأ من lead في CRM وتنتهي بحجز وخطة دفعات.

Demo flow:

1. افتح CRM lead.
2. حوّل lead إلى فرصة أو حجز.
3. افتح مشروع عقاري، مبنى، دور، وحدة.
4. اعرض Unit type / attached areas.
5. اعرض Reservation.
6. اعرض Payment Plan.
7. اعرض sales order أو invoice/payment.

Key modules:

```text
real_estate
real_estate_crm
realestate_project
property_coding
payment_analytic_account
```

Sales angle:

> النظام يربط المبيعات بالعقار والتحصيلات، مع تحكم في الوحدات وخطط الدفع.

## 4. Saudi HR Demo

Opening:

> هذه قاعدة مستقلة لإدارة موارد بشرية سعودية: حضور، جزاءات، مكافآت، عهد، قروض، تأمينات، ونهاية خدمة.

Demo flow:

1. افتح ملف موظف.
2. اعرض attendance code أو attendance rules.
3. اعرض contract work hours.
4. أنشئ bonus أو penalty.
5. اعرض custody.
6. اعرض loan.
7. اعرض Saudi EOS أو social insurance.

Key modules:

```text
attendances_structure_base
attendance_rules
employee_bonuses
employee_penalty
hr_custody
ohrms_loan
saudi_hr_eos
social_insurance
```

Sales angle:

> HR جاهز للسوق السعودي مع إضافات عملية حول الحضور والعهد والقروض ونهاية الخدمة.

## 5. Education / EduSaaS Demo

Opening:

> هذا الديمو يعرض بوابة تعليمية خارجية مرتبطة بمنصة SaaS، ويمكن تحويلها لاحقا إلى Odoo-native modules.

Demo flow:

1. افتح dashboard التعليمي.
2. اعرض lessons.
3. اعرض exams.
4. اعرض assignments.
5. اعرض live sessions.
6. اربط الاشتراك من Master SaaS.
7. اختم بفكرة portal للطلاب وأولياء الأمور.

Key source:

```text
edusaas-project-source
React/Vite frontend
API server routes
```

Sales angle:

> التعليم يمكن بيعه كبوابة SaaS متخصصة، حتى لو كان خارج Odoo في المرحلة الأولى.
