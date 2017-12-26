# -*- coding: utf-8 -*-

from openerp import models, fields, api


class AccountFiscalyearCloseState(models.TransientModel):
    """
    Closes  Account Fiscalyear
    """
    _name = "account.fiscalyear.close.state"
    _description = "Fiscalyear Close state"

    fy_id = fields.Many2one('account.fiscalyear',
                            'Fiscal Year to Close',
                            required=True,
                            help="Select a fiscal year to close")


    @api.multi
    def data_save(self):
        """
        This function close account fiscalyear
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of Account fiscalyear close state’s IDs

        """
        journal_period_obj = self.env['account.journal.period']
        period_obj = self.env['account.period']
        fiscalyear_obj = self.env['account.fiscalyear']
        account_move_obj = self.env['account.move']

        for fy_id in self:
            #fy_id = data['fy_id'][0]

            account_move_ids = account_move_obj.search([('period_id.fiscalyear_id', '=', fy_id), ('state', '=', "draft")])
            if account_move_ids:
                raise osv.except_osv(_('Invalid Action!'), _('In order to close a fiscalyear, you must first post related journal entries.'))

            cr.execute('UPDATE account_journal_period ' \
                        'SET state = %s ' \
                        'WHERE period_id IN (SELECT id FROM account_period \
                        WHERE fiscalyear_id = %s)',
                    ('done', fy_id))
            cr.execute('UPDATE account_period SET state = %s ' \
                    'WHERE fiscalyear_id = %s', ('done', fy_id))
            cr.execute('UPDATE account_fiscalyear ' \
                    'SET state = %s WHERE id = %s', ('done', fy_id))
            self.invalidate_cache()

            return {'type': 'ir.actions.act_window_close'}