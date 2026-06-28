
from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError, Warning


class PayslipAttendance(models.TransientModel):
    """
        Initialize Payslip Attendance:
         -
    """
    _name = 'payslip.attendance'
    _description = 'Payslip Attendance'

    employee_id = fields.Many2one(
        'hr.employee',
    )
    hr_payslip_id = fields.Many2one(
        'hr.payslip',
        domain="[('state', '=', 'done')]"
    )
    
    def action_view_onscreen(self):
        """ Action View Onscreen """
        for rec in self:
            attendance = self.env['hr.payslip.attendance'].search(
                [('rule_id', '=', rec.hr_payslip_id.id)])
            action = self.env.ref('attendances_structure_base.hr_payslip_attendance_action').read()[0]
            action['domain'] = [('id', '=', attendance.ids)]
            return action

