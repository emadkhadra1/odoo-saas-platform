from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
import xlrd
try:
    from pyxlsb import convert_date
except ImportError:
    from datetime import datetime, timedelta

    def convert_date(value):
        return datetime(1899, 12, 30) + timedelta(days=float(value))
import base64


class BusinessItemImport(models.TransientModel):
    _name = 'b2b.business.items.import.wiz'

    sheet_import = fields.Binary(string="Upload File")
    sheet_import_filename = fields.Char()

    def import_data(self):
        workbook = xlrd.open_workbook(file_contents=base64.decodestring(self.sheet_import))
        sheet = workbook.sheet_by_index(0)
        row_count = sheet.nrows
        col_count = sheet.ncols
        header_list = []
        assay_dict = {}
        assay_line_list = []
        for header_row in range(0, 1):
            for header_col in range(0, col_count):
                cell = sheet.cell(header_row, header_col)
                header_list.append(cell.value)
        for cur_row in range(1, row_count):
            cell_name = sheet.cell(cur_row, header_list.index('Title'))
            if cell_name and cell_name.value:
                assay_dict['name'] = cell_name.value
            # number_of_criteria = sheet.cell(cur_row, header_list.index('Code'))
            # if number_of_criteria and number_of_criteria.value:
            #     assay_dict['code'] = number_of_criteria.value
            project_name = sheet.cell(cur_row, header_list.index('Sub Business Statement'))
            if project_name and project_name.value:
                project_id = self.env['b2b.sub.business.items'].search([('name', '=', project_name.value)])
                if project_id:
                    assay_dict['sub_business_statement_id'] = project_id.id
                # else:
                #     raise ValidationError("برجاء التأكد من صحة اسم المشروع")
            unit_name = sheet.cell(cur_row, header_list.index('Unit'))
            if unit_name and unit_name.value:
                unit_id = self.env['uom.uom'].search([('name', '=', unit_name.value)], limit=1)
                if unit_id:
                    assay_dict['uom_id'] = unit_id.id
                else:
                    raise ValidationError("برجاء التأكد من صحة اسم وحدة القياس")
            branch_name = sheet.cell(cur_row, header_list.index('Creation Date'))
            if branch_name and branch_name.value:
                assay_dict['creation_date'] = format(convert_date(branch_name.value), '%Y-%m-%d') if branch_name.value else False
            assay_id = self.env['b2b.business.items'].create(assay_dict)


class ConstructionBOQImport(models.TransientModel):
    _name = 'b2b.construction.boq.import.wiz'

    sheet_import = fields.Binary(string="Upload File")
    sheet_import_filename = fields.Char()

    def import_data(self):
        workbook = xlrd.open_workbook(file_contents=base64.decodestring(self.sheet_import))
        sheet = workbook.sheet_by_index(0)
        row_count = sheet.nrows
        col_count = sheet.ncols
        header_list = []
        assay_dict = {}
        for header_row in range(0, 1):
            for header_col in range(0, col_count):
                cell = sheet.cell(header_row, header_col)
                header_list.append(cell.value)
        assay_id = False
        for cur_row in range(1, row_count):
            assay_line_list = []
            cell_name = False
            cell_name = sheet.cell(cur_row, header_list.index('Contractor Quotation'))
            if cell_name and cell_name.value:
                assay_dict['name'] = cell_name.value
            type_name = sheet.cell(cur_row, header_list.index('Construction Type'))
            if type_name and type_name.value:
                type_id = self.env['b2b.constrution.type'].search([('name', '=', type_name.value)], limit=1)
                if type_id:
                    assay_dict['construction_type_id'] = type_id.id
                else:
                    raise ValidationError(f"'{type_name}' برجاء التأكد من صحة نوع المشروع")
            project_name = sheet.cell(cur_row, header_list.index('Project Name'))
            if project_name and project_name.value:
                project_id = self.env['construction.project'].search([('name', '=', project_name.value)])
                if project_id:
                    assay_dict['project_id'] = project_id.id
                else:
                    raise ValidationError(f"'{project_name}' برجاء التأكد من صحة اسم المشروع")
            date = sheet.cell(cur_row, header_list.index('Date'))
            if date and date.value:
                assay_dict['date_order'] = format(convert_date(date.value), '%Y-%m-%d') if date.value else False
            if cell_name and cell_name.value:
                assay_id = self.env['b2b.construction.boq'].create(assay_dict)
            if assay_id:
                line_dict = {}
                business_item = sheet.cell(cur_row, header_list.index('BOQ Item/Business Statement'))
                if business_item and business_item.value:
                    business_statement_id = self.env['b2b.business.items'].search([('name', '=', business_item.value)], limit=1)
                    if business_statement_id:
                        line_dict['business_statement_id'] = business_statement_id.id
                        line_dict['sub_business_statement_id'] = business_statement_id.sub_business_statement_id.id
                        line_dict['sub_item_id'] = business_statement_id.sub_item_id.id
                        line_dict['main_item_id'] = business_statement_id.main_item_id.id
                    else:
                        raise ValidationError(f"'{business_item}' برجاء التأكد من صحة اسم بند الأعمال")
                if 'BOQ Item/Business Statement/Unit' in header_list:
                    unit_name = sheet.cell(cur_row, header_list.index('BOQ Item/Business Statement/Unit'))
                else:
                    unit_name = sheet.cell(cur_row, header_list.index('BOQ Item/Unit'))
                if unit_name and unit_name.value:
                    unit_id = self.env['uom.uom'].search([('name', '=', unit_name.value)])
                    if unit_id:
                        line_dict['uom_id'] = unit_id.id
                    else:
                        raise ValidationError(f"'{business_item}' برجاء التأكد من صحة اسم وحدة القياس")
                category = sheet.cell(cur_row, header_list.index('BOQ Item/Category'))
                if category and category.value:
                    line_dict['category'] = float(category.value)
                required_quantity = sheet.cell(cur_row, header_list.index('BOQ Item/Required Quantity'))
                if required_quantity and required_quantity.value:
                    line_dict['required_quantity'] = float(required_quantity.value)
                assay_line_list.append([0, 0, line_dict])
                assay_id.write({'indexation_ids': assay_line_list})
