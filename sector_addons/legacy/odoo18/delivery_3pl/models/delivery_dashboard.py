from odoo import models, fields, api
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta


class DeliveryDashboard(models.AbstractModel):
    _name = 'delivery.dashboard'
    _description = 'Delivery Dashboard Data Provider'

    @api.model
    def get_dashboard_data(self, date_from=False, date_to=False):
        today = date.today()
        if not date_from:
            date_from = today.replace(day=1)
        else:
            date_from = fields.Date.from_string(date_from)
        if not date_to:
            date_to = today
        else:
            date_to = fields.Date.from_string(date_to)

        prev_start = date_from - relativedelta(months=1)
        prev_end = date_to - relativedelta(months=1)

        Company = self.env['delivery.company']
        Branch = self.env['delivery.company.branch']
        Rider = self.env['delivery.rider']
        Contract = self.env['delivery.contract']
        Settlement = self.env['delivery.settlement']

        user = self.env.user
        is_admin = user.has_group('delivery_3pl.group_delivery_admin')

        if not is_admin:
            my_companies = Company.search([('operations_manager_id', '=', user.id)])
            if my_companies:
                company_ids = my_companies.ids
            else:
                company_ids = []
        else:
            my_companies = False
            company_ids = False

        company_domain = [('is_active', '=', True)]
        branch_domain = [('is_active', '=', True)]
        rider_domain = []
        contract_domain = [('status', '=', 'active')]
        if not is_admin:
            if company_ids:
                company_domain.append(('id', 'in', company_ids))
                branch_domain.append(('company_id', 'in', company_ids))
                rider_domain.append(('primary_company_id', 'in', company_ids))
                contract_domain.append(('company_id', 'in', company_ids))
            else:
                company_domain.append(('id', '=', 0))
                branch_domain.append(('company_id', '=', 0))
                rider_domain.append(('primary_company_id', '=', 0))
                contract_domain.append(('company_id', '=', 0))

        total_companies = Company.search_count(company_domain)
        total_branches = Branch.search_count(branch_domain)
        total_riders = Rider.search_count(rider_domain)
        active_riders = Rider.search_count(rider_domain + [('status', '=', 'active')])
        inactive_riders = Rider.search_count(rider_domain + [('status', '=', 'inactive')])
        suspended_riders = Rider.search_count(rider_domain + [('status', '=', 'suspended')])
        active_contracts = Contract.search_count(contract_domain)

        settlement_domain = [
            ('period_start', '>=', date_from),
            ('period_end', '<=', date_to),
        ]
        if not is_admin:
            settlement_domain.append(('company_id', 'in', company_ids or [0]))
        settlements = Settlement.search(settlement_domain)
        total_orders = sum(s.total_orders for s in settlements)
        total_gross = sum(s.gross_amount for s in settlements)
        total_net = sum(s.net_amount for s in settlements)
        total_penalties = sum(s.penalties for s in settlements)
        total_bonuses = sum(s.bonuses for s in settlements)

        prev_settlement_domain = [
            ('period_start', '>=', prev_start),
            ('period_end', '<=', prev_end),
        ]
        if my_companies and not is_admin:
            prev_settlement_domain.append(('company_id', 'in', my_companies.ids))
        prev_settlements = Settlement.search(prev_settlement_domain)
        prev_orders = sum(s.total_orders for s in prev_settlements)
        prev_gross = sum(s.gross_amount for s in prev_settlements)
        prev_net = sum(s.net_amount for s in prev_settlements)

        orders_growth = self._calc_growth(total_orders, prev_orders)
        gross_growth = self._calc_growth(total_gross, prev_gross)
        net_growth = self._calc_growth(total_net, prev_net)

        status_base = []
        if my_companies and not is_admin:
            status_base = [('company_id', 'in', my_companies.ids)]
        settlements_by_status = {
            'draft': Settlement.search_count(status_base + [('status', '=', 'draft')]),
            'pending': Settlement.search_count(status_base + [('status', '=', 'pending_approval')]),
            'approved': Settlement.search_count(status_base + [('status', '=', 'approved')]),
            'locked': Settlement.search_count(status_base + [('status', '=', 'locked')]),
        }

        company_data = []
        companies = Company.search(company_domain, limit=20)
        for comp in companies:
            comp_settlements = settlements.filtered(lambda s: s.company_id.id == comp.id)
            company_data.append({
                'id': comp.id,
                'name': comp.name,
                'name_ar': comp.name_ar or comp.name,
                'branches': len(comp.branch_ids.filtered('is_active')),
                'riders': len(comp.rider_ids.filtered(lambda r: r.status == 'active')),
                'contracts': len(comp.contract_ids.filtered(lambda c: c.status == 'active')),
                'orders': sum(s.total_orders for s in comp_settlements),
                'gross': sum(s.gross_amount for s in comp_settlements),
                'net': sum(s.net_amount for s in comp_settlements),
            })

        branch_data = []
        branches = Branch.search(branch_domain, limit=30)
        for br in branches:
            br_settlements = settlements.filtered(lambda s: s.branch_id.id == br.id)
            branch_data.append({
                'id': br.id,
                'name': br.name,
                'company': br.company_id.name,
                'riders': len(br.rider_ids.filtered(lambda r: r.status == 'active')),
                'orders': sum(s.total_orders for s in br_settlements),
                'gross': sum(s.gross_amount for s in br_settlements),
            })

        recent_settlements = Settlement.search(status_base, order='create_date desc', limit=10)
        recent_list = []
        for s in recent_settlements:
            recent_list.append({
                'id': s.id,
                'number': s.settlement_number,
                'company': s.company_id.name,
                'branch': s.branch_id.name or '-',
                'status': s.status,
                'period': '%s → %s' % (
                    fields.Date.to_string(s.period_start),
                    fields.Date.to_string(s.period_end),
                ),
                'orders': s.total_orders,
                'gross': s.gross_amount,
                'net': s.net_amount,
            })

        Penalty = self.env['delivery.rider.penalty']
        penalty_domain = [
            ('date', '>=', date_from),
            ('date', '<=', date_to),
        ]
        if not is_admin:
            penalty_domain.append(('rider_id.primary_company_id', 'in', company_ids or [0]))
        total_penalty_count = Penalty.search_count(penalty_domain)

        return {
            'kpis': {
                'total_companies': total_companies,
                'total_branches': total_branches,
                'total_riders': total_riders,
                'active_riders': active_riders,
                'inactive_riders': inactive_riders,
                'suspended_riders': suspended_riders,
                'active_contracts': active_contracts,
                'total_orders': total_orders,
                'total_gross': round(total_gross, 2),
                'total_net': round(total_net, 2),
                'total_penalties': round(total_penalties, 2),
                'total_bonuses': round(total_bonuses, 2),
                'orders_growth': orders_growth,
                'gross_growth': gross_growth,
                'net_growth': net_growth,
                'penalty_count': total_penalty_count,
            },
            'settlements_by_status': settlements_by_status,
            'company_data': company_data,
            'branch_data': branch_data,
            'recent_settlements': recent_list,
            'date_from': fields.Date.to_string(date_from),
            'date_to': fields.Date.to_string(date_to),
        }

    def _calc_growth(self, current, previous):
        if previous and previous > 0:
            return round(((current - previous) / previous) * 100, 1)
        elif current > 0:
            return 100.0
        return 0.0
