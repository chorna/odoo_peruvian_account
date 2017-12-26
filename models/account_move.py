# -*- coding: utf-8 -*-

from openerp import models, fields


class AccountMoveInherit(models.Model):
    _inherit = "account.move"

    period_id = fields.Many2one('account.period', 'Periodo', required=True,
                                states={'posted':[('readonly',True)]},
                                )

    #def _get_period(self):
        #ctx = dict(context or {})
        #period_id = self.env['account.period'].search([('state', '=', 'draft')], limit=1, order='date_start')
        #return period_id