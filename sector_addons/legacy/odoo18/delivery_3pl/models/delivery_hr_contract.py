from odoo import models, fields, api


class HrContractDeliveryRider(models.Model):
    _inherit = 'hr.contract'

    is_delivery_rider = fields.Boolean(string='Delivery Rider (مندوب توصيل)',
                                        help='إذا كان هذا العقد لمندوب توصيل داخلي، سيتم إنشاء سجل مندوب تلقائياً')
    delivery_company_id = fields.Many2one('delivery.company', string='Delivery Company (شركة التوصيل)')
    delivery_branch_id = fields.Many2one('delivery.company.branch', string='Delivery Branch (الفرع)',
                                          domain="[('company_id', '=', delivery_company_id)]")
    delivery_rider_id = fields.Many2one('delivery.rider', string='Linked Rider (المندوب المرتبط)',
                                         readonly=True, copy=False)

    @api.onchange('delivery_company_id')
    def _onchange_delivery_company(self):
        if self.delivery_company_id:
            self.delivery_branch_id = False

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if rec.is_delivery_rider and not rec.delivery_rider_id and rec.employee_id:
                rec._create_delivery_rider()
        return records

    def write(self, vals):
        res = super().write(vals)
        if vals.get('is_delivery_rider'):
            for rec in self:
                if rec.is_delivery_rider and not rec.delivery_rider_id and rec.employee_id:
                    rec._create_delivery_rider()
        return res

    def _create_delivery_rider(self):
        self.ensure_one()
        emp = self.employee_id
        if not emp:
            return

        rider_type = self.env['delivery.rider.type'].search([('type', '=', 'internal')], limit=1)

        rider_vals = {
            'name': emp.name,
            'phone': emp.work_phone or emp.mobile_phone or 'N/A',
            'national_id': emp.identification_id or '',
            'rider_type_id': rider_type.id if rider_type else False,
            'primary_company_id': self.delivery_company_id.id if self.delivery_company_id else False,
            'branch_id': self.delivery_branch_id.id if self.delivery_branch_id else False,
            'status': 'active',
            'join_date': self.date_start or fields.Date.today(),
            'work_start_date': self.date_start or fields.Date.today(),
        }

        rider = self.env['delivery.rider'].create(rider_vals)
        self.delivery_rider_id = rider.id

    def action_view_rider(self):
        self.ensure_one()
        if self.delivery_rider_id:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Delivery Rider',
                'res_model': 'delivery.rider',
                'view_mode': 'form',
                'res_id': self.delivery_rider_id.id,
            }
