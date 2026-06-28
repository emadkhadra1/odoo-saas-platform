from odoo import models, fields, api
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    sequence_generated = fields.Boolean(string="Sequence Generated", copy=False)

    @api.depends('posted_before', 'state', 'journal_id', 'date')
    def _compute_name(self):
        for move in self:
            if not move.journal_id.sequence_id:
              return super(AccountMove, self)._compute_name()
            sequence_id = move.with_company(move.company_id).with_context(company_id=move.company_id.id)._get_sequence()
            if not sequence_id:
                raise UserError('Please define a sequence on your journal.')
            if not move.sequence_generated and move.state == 'draft':
                move.name = '/'
            elif not move.sequence_generated and move.state != 'draft':
                date = False
                if move.invoice_date:
                    date = move.invoice_date
                elif move.date:
                    date = move.date
                move.name = sequence_id.with_company(move.company_id).with_context({'ir_sequence_date': date, 'bypass_constrains': True, 'company': move.company_id, 'company_id': move.company_id.id}, company_id=move.company_id).next_by_id(sequence_date=date)
                move.sequence_generated = True

    @api.model
    def _autopost_draft_entries(self):
        ''' This method is called from a cron job.
        It is used to post entries such as those created by the module
        account_asset.
        '''
        companies = self.env['res.company'].search([])
        for company in companies:
            records = self.search([
                ('state', '=', 'draft'),
                ('date', '<=', fields.Date.context_today(self)),
                ('auto_post', '=', True),
                ('company_id', '=', company.id),
            ])

            for ids in self._cr.split_for_in_conditions(records.ids, size=1000):
                self.with_company(company).with_context(company_id=company.id).browse(ids)._post()
                if not self.env.registry.in_test_mode():
                    self._cr.commit()

    def _get_sequence(self):
        ''' Return the sequence to be used during the post of the current move.
        :return: An ir.sequence record or False.
        '''
        self.ensure_one()

        journal = self.journal_id
        if self.move_type in ('entry', 'out_invoice', 'in_invoice', 'out_receipt', 'in_receipt') or not journal.refund_sequence:
            return journal.sequence_id
        if not journal.refund_sequence_id:
            return
        return journal.refund_sequence_id

    # def _get_invoice_computed_reference(self):
    #     self.ensure_one()
    #     if self.journal_id.invoice_reference_type == 'none':
    #         return ''
    #     else:
    #         ref_function = getattr(self, '_get_invoice_reference_{}_{}'.format(self.journal_id.invoice_reference_model, self.journal_id.invoice_reference_type))
    #         if ref_function:
    #             return ref_function()
    #         else:
    #             raise UserError(_('The combination of reference model and reference type on the journal is not implemented'))

