from odoo import fields, models, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    custody_account_id = fields.Many2one(comodel_name='account.account',string='Custody Account')
    employee_id = fields.Many2one(comodel_name='hr.employee',string='Employee')
class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    partner_id = fields.Many2one(comodel_name='res.partner', string='Partner')

    def create_employee_partner(self):
        for rec in self:
            if not rec.partner_id:
                partner = self.env['res.partner'].create({
                    'name': rec.name,
                    'company_type': 'person',
                    'email': rec.work_email,
                    'mobile': rec.mobile_phone,
                    'employee_id': rec.id
                })
                rec.partner_id = partner.id

    @api.model
    def create(self, vals_list):
        res = super(HrEmployee, self).create(vals_list)
        partner = self.env['res.partner'].create({
            'name': res.name,
            'company_type': 'person',
            'email': res.work_email,
            'mobile': res.mobile_phone,
            'employee_id': res.id
        })
        res.partner_id = partner.id
        return res

    # def write(self, vals):
    #     res = super(HrEmployee,self).write(vals)
    #     if 'name' in vals:
    #         res.partner_id.write({'name': vals['name']})
    #     if 'work_email' in vals:
    #         res.partner_id.write({'email': vals['work_email']})
    #     if 'mobile_phone' in vals:
    #         res.partner_id.write({'mobile': vals['mobile_phone']})

    def unlink(self):
        for rec in self:
            if rec.partner_id:
                rec.partner_id.unlink()
        return super(HrEmployee, self).unlink()
