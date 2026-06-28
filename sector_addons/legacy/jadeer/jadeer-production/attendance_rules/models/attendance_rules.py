# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp


class AttendanceRules(models.Model):
    _name = 'attendance.deduction.rules'
    _rec_name = 'name'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    name = fields.Char(compute="_compute_name")
    code = fields.Char('Code', copy=True)
    duration_type = fields.Selection([
        ('late', 'Late Check in'),
        ('early', 'Early Checkout'),
        ('no_check', 'No Checkout'),
        ('absent', 'Absent')
    ], default='late', string='Type', copy=True)
    remaining = fields.Boolean(string='Actual Late Minutes', copy=True)
    duration = fields.Float(string='Duration', copy=True)
    from_time = fields.Float(string='From', copy=True)
    to_time = fields.Float(string='To', copy=True)
    structure_ids = fields.Many2many('attendance.structure', string='Attendance Structure')
    line_ids = fields.One2many(comodel_name="attendance.deduction.rules.line", inverse_name="rule_id", string="Lines",
                               required=False, )
    penalty_base = fields.Selection(string="Penalty Base", selection=[
        ('hour', 'Hour'),
        ('day', 'Day'),
    ], required=True, default='day')

    def copy(self, default=None):
        self.ensure_one()
        chosen_name = default.get('code') if default else ''
        new_name = chosen_name or _('%s (copy)') % self.code
        default = dict(default or {}, code=new_name)
        return super(AttendanceRules, self).copy(default)

    @api.depends('from_time', 'to_time')
    def _compute_name(self):
        for rec in self:
            if rec.duration_type != 'absent':
                rec.name = " Time " + (str(rec.duration_type) + " From (" + (
                        str('{0:02.0f}:{1:02.0f}'.format(*divmod(float(rec.from_time) * 60, 60))) + " )To (" + str(
                    '{0:02.0f}:{1:02.0f}'.format(*divmod(float(rec.to_time) * 60,
                                                         60))) + " )") if not rec.remaining else "Actual Late Minutes")
            else:
                rec.name = " Absent Rule"

    def get_penalty(self, repetition, hours_per_day, actual_time=0.0):
        if self.remaining and self.duration_type != 'absent':
            return actual_time
        if repetition:
            res = self.line_ids.filtered(lambda l: l.repetition == repetition)
            if res:
                if self.penalty_base == 'hour':
                    return res.apply_hours
                else:
                    return res.apply_days * hours_per_day
            if self.line_ids.sorted(key='repetition'):
                last_line = self.line_ids.sorted(key='repetition')[-1]
                if repetition > last_line.repetition:
                    if self.penalty_base == 'hour':
                        return last_line.apply_hours
                    else:
                        return last_line.apply_days * hours_per_day
            return 0.0
        return 0.0


class AttendanceRulesLines(models.Model):
    _name = 'attendance.deduction.rules.line'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    rule_id = fields.Many2one(comodel_name="attendance.deduction.rules", string="Rule", required=False, )
    apply_dedication = fields.Float(string='Apply Deduction(Hours)', copy=True)
    apply_absent_day = fields.Float(string='Apply Deduction(Days)', copy=True)
    repetition = fields.Integer(string='Repetition', required=True, copy=True, default=1)
    apply_hours = fields.Float(string='Apply Deduction(Hours)', copy=True)
    apply_days = fields.Float(string='Apply Deduction(Days)', copy=True)


class AttendanceStructure(models.Model):
    _name = 'attendance.structure'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    name = fields.Char()
    permission = fields.Float(string="Permission Minutes", required=False, )
    structure_ids = fields.Many2many('attendance.deduction.rules', string='Attendance Rules')
    flixable_hours = fields.Float()
    permision_type = fields.Selection([('daily', 'Daily'), ('monthly', 'Monthly')])
    work_day_rate = fields.Float(string='Work Day Over Time Rate')
    public_leave_rate = fields.Float(string='Public Leave Over Time Rate')
    weekly_leave_rate = fields.Float(string='Weekly Leave Over Time Rate')
    overtime_start_limit = fields.Float(string='Over Time Start Limit')
    use_day_night_overtime = fields.Boolean(string='Use day/night overtime')
    work_night_rate = fields.Float(string='Work Night Over Time Rate')
    overtime_start_night_limit = fields.Float(string='Over Time Start Night Limit')

    @api.constrains('structure_ids')
    def _check_structure_ids(self):
        if self.structure_ids:
            late_int_rules = self.structure_ids.filtered(lambda c: c.duration_type == 'late').mapped('remaining')
            late_out_rules = self.structure_ids.filtered(lambda c: c.duration_type == 'early').mapped('remaining')
            if len(set(late_int_rules)) > 1 or len(set(late_out_rules)) > 1:
                raise exceptions.ValidationError('Selected Rules Must be all type [Actual Late Minutes] or Not')
