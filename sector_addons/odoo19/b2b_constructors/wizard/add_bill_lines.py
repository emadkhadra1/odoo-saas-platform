from odoo import api, fields, models 


class AddBillLines(models.TransientModel):
    _name = 'add.bill.lines'
    _rec_name = 'name'
    _description = 'Add Bill Lines'

    name = fields.Char(string="Name", required=False, )
    project_id = fields.Many2one(related='bill_id.project_id')
    bill_id = fields.Many2one(comodel_name="b2b.progress.bill", string="Progress Bill", required=True, )
    entrepreneurs_ids = fields.Many2many(comodel_name="b2b.entrepreneurs", relation="bill_lines_entrepreneurs_rel",
                                         column1="add_bill_line_id", column2="entrepreneurs_id", string="Business Statement")
    
    def action_assign(self):
        env_bill_lines = self.env['b2b.progress.bill.lines2']
        bill_obj = self.bill_id
        for entr in self.entrepreneurs_ids:
            values = {'main_item_id': entr.main_item_id.id, 'sub_item_id': entr.sub_item_id.id,
                      'sub_business_statement_id': entr.sub_business_statement_id.id,
                      'business_statement_id': entr.business_statement_id.id, 'progress_bill_id': bill_obj.id}
            env_bill_lines.create(values)
