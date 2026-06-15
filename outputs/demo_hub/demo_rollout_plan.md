# SaaS Demo Rollout Plan

## Objective

Build a complete sales/demo experience with:

- Marketing website
- Master SaaS backend
- Sector-specific tenant demos
- Demo data
- SaaS plans mapped to real modules

## Phase A - Master SaaS Demo

1. Install `odoo_saas_manager` in `master_saas`.
2. Enable Website and CRM.
3. Load the sector SaaS plans from `demo/saas_plan_demo.xml`.
4. Configure:
   - `saas_manager.template_database`
   - `saas_manager.public_domain`
   - `saas_manager.api_key`
5. Create demo tenants:
   - Al Riyada Contracting
   - Fast Mile Logistics
   - Jadeer Properties
   - Saudi People Co.
   - EduSaaS Academy

## Phase B - Sector Tenant Templates

Create one template database per sector:

```text
template_3pl
template_construction
template_realestate
template_saudi_hr
template_education
```

Each template should include:

- Base Odoo configuration
- Arabic/English language if needed
- Company template data
- Sector modules
- `saas_tenant_agent`
- Demo admin account

## Phase C - Demo Data

Each sector needs a 10-minute story:

- One customer/company
- One operational cycle
- One invoice/payment
- One dashboard or report
- One import/onboarding example

## Phase D - Website Conversion

Move the current static demo hub into either:

1. Odoo Website pages on `master_saas`, or
2. A separate Next.js/React website that calls the SaaS API.

Recommended first step: Odoo Website, because it connects quickly to CRM leads and pricing.

## Phase E - Sales Flow

Customer flow:

```text
Landing page -> Select sector -> Select plan -> Request demo -> CRM lead -> Create tenant -> Send URL
```

Admin flow:

```text
SaaS Manager -> Tenant -> Provision -> Upload onboarding file -> Activate subscription -> Invoice/payment
```

## Deliverables

- Master backend demo
- Five sector landing pages
- Five tenant demo databases
- Pricing table
- Demo scripts
- Compatibility notes
- Upgrade backlog for legacy modules
