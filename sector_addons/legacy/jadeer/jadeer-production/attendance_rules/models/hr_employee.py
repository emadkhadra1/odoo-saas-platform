from datetime import datetime, timedelta
from odoo import api, fields, models, _
from odoo import SUPERUSER_ID
import pytz


class Employee(models.Model):
    _inherit = 'hr.employee'

    attendance_id = fields.Many2one(related='resource_calendar_id.attendance_id', string='Attendance Structure')
