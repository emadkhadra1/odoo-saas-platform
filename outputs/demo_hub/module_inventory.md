# SingleClic SaaS Demo Inventory

هذا التقرير مختصر مبني على قراءة ملفات الأرشيف التي ذكرتها، بدون تثبيت فعلي داخل Odoo.

## 3PL / Logistics

- Archive: `delivery_3pl_v4.6.0.zip`
- Main addon: `delivery_3pl`
- Version: `18.0.4.6.0`
- Name: `3PL Delivery Operations Management`
- Depends: `base`, `mail`, `web`, `hr_contract`, `fleet`, `hr_payroll`
- Demo focus:
  - Delivery companies
  - Riders
  - Contracts and tiers
  - Pricing
  - Settlements
  - Performance dashboard

## Construction

- Archive: `emad_construction_odoo19_modules_ready.zip`
- Main addons:
  - `b2b_constructors`
  - `b2b_constructor_edit`
  - `construction_project`
  - `construction_budgeting`
  - `construction_project_reports`
  - `financial_custody`
  - `hr_custody`
- Target shown in manifests: Odoo `19.0.1.0.0`
- Important dependencies:
  - `account`
  - `om_account_accountant`
  - `purchase`
  - `purchase_requisition`
  - `project`
  - `stock`
  - `sale_management`
  - `stock_analytic`
- Demo focus:
  - BOQ
  - Project management
  - Progress bills
  - Owner/contractor extracts
  - Construction reports
  - Budgeting

## Real Estate / Jadeer

- Archive: `jadeer-production.zip`
- Important addons detected:
  - `real_estate`
  - `real_estate_crm`
  - `realestate_project`
  - `real_estate_security`
  - `property_coding`
  - `project_phase_building_floor`
  - `partner_custom`
  - `payment_analytic_account`
- Real Estate depends include:
  - `account`
  - `crm`
  - `sale_management`
  - `sale_crm`
  - `realestate_project`
  - `payment_analytic_account`
  - `project_phase_building_floor`
  - `partner_custom`
  - `real_estate_security`
  - `web_notify`
- Demo focus:
  - Real estate CRM
  - Units and projects
  - Reservations
  - Payment plans
  - Sales orders
  - Batch payments

## Saudi HR

- Archive: `saudi hr.rar`
- Addons detected:
  - `attendances_structure_base`
  - `attendance_rules`
  - `contract_work_hour`
  - `employee_bonuses`
  - `employee_custom`
  - `employee_penalty`
  - `hr_custody`
  - `hr_employee_attendace_code`
  - `hr_employee_custom`
  - `hr_multi_shift`
  - `import_attendance`
  - `ohrms_loan`
  - `ohrms_loan_accounting`
  - `ohrms_loan_custom`
  - `res_documents`
  - `salary_structure_demo`
  - `saudi_hr_eos`
  - `saudi_hr_iqama`
  - `social_insurance`
- Demo focus:
  - Attendance rules
  - Payroll-related attendance
  - Bonuses and penalties
  - Custody
  - Loans
  - Saudi documents/Iqama
  - End of service
  - Social insurance

## Education / EduSaaS

- Archive: `edusaas-project-source.tar.gz`
- Detected type: React/Vite frontend plus API server source, not an Odoo addon.
- Detected API areas:
  - dashboard
  - subscriptions
  - analytics
  - notifications
  - lessons
  - exams
  - assignments
  - live sessions
- Recommended path:
  - Use as external education portal integrated with Odoo SaaS API, or
  - Convert into Odoo modules later if the tenant must stay fully inside Odoo.

## SaaS Plan Mapping Proposal

Starter:

```text
base,mail,contacts,saas_tenant_agent
```

Construction Business:

```text
base,mail,contacts,account,project,purchase,stock,construction_project,b2b_constructors,construction_budgeting,construction_project_reports,saas_tenant_agent
```

3PL Business:

```text
base,mail,web,hr_contract,fleet,hr_payroll,delivery_3pl,saas_tenant_agent
```

Real Estate Business:

```text
base,mail,crm,sale_management,account,realestate_project,real_estate,real_estate_crm,property_coding,saas_tenant_agent
```

Saudi HR Business:

```text
base,mail,hr,hr_payroll,attendances_structure_base,attendance_rules,employee_bonuses,employee_penalty,hr_custody,ohrms_loan,saudi_hr_eos,saas_tenant_agent
```

Education:

```text
base,mail,contacts,website,portal,saas_tenant_agent
```

مع ربط خارجي أو تحويل لاحق لمشروع EduSaaS.
