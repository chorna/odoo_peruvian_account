# *-* coding: utf-8 *-*

from openerp import fields, models, api


class AccountPeriodClose(models.TransientModel):
    """
        close period
    """
    _name = "account.period.close"
    _description = "period close"

    sure = fields.Boolean('Check this box')

    @api.multi
    def data_save(self, context=None):
        """
        This function close period
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: account period close’s ID or list of IDs
         """
        journal_period_pool = self.env['account.journal.period']
        period_pool = self.env['account.period']
        account_move_obj = self.env['account.move']

        cr = self.env.cr
        mode = 'done'
        for form in self:
            if form['sure']:
                for id in context['active_ids']:
                    account_move_ids = account_move_obj.search([
                        ('period_id', '=', form.id), ('state', '=', "draft")])
                    if account_move_ids:
                        raise osv.except_osv(_('Invalid Action!'), _('In order to close a period, you must first post related journal entries.'))

                    cr.execute('update account_journal_period set state=%s where period_id=%s', (mode, id))
                    cr.execute('update account_period set state=%s where id=%s', (mode, id))
                    self.invalidate_cache()

        return {'type': 'ir.actions.act_window_close'}