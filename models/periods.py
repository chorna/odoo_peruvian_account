# -*- coding: utf-8 -*-

from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import fields, models, api


class AccountFiscalYear(models.Model):
    _name = "account.fiscalyear"
    _description = "Fiscal Year"

    name = fields.Char('Nombre', required=True)
    code = fields.Char(u'Código', size=6, required=True)
    company_id = fields.Many2one('res.company', 'Company', required=True,
                                 default=lambda self: self.env.user.company_id)
    date_start = fields.Date('Inicio', required=True)
    date_stop = fields.Date('Fin', required=True)
    period_ids = fields.One2many('account.period', 'fiscalyear_id', 'Periods')
    state = fields.Selection(
        [('draft','Open'), ('done','Closed')],
        'Status',
        readonly=True,
        copy=False,
        default='draft'
    )
    end_journal_period_id = fields.Many2one(
        'account.journal.period', 'End of Year Entries Journal',
        readonly=True, copy=False)

    _order = "date_start, id"

    def create_period3(self):
        return self.create_period(interv=3)

    @api.multi
    def create_period(self, context=None, interv=1):
        period_obj = self.env['account.period']
        for fy in self:
            ds = datetime.strptime(fy.date_start, '%Y-%m-%d')
            de = datetime.strptime(fy.date_stop, '%Y-%m-%d')
            period_obj.create({
                    'name':  "%s %s" % ('Opening Period', ds.strftime('%Y')),
                    'code': ds.strftime('00/%Y'),
                    'date_start': ds,
                    'date_stop': ds,
                    'special': True,
                    'fiscalyear_id': fy.id,
                })
            while ds.strftime('%Y-%m-%d') < fy.date_stop:
                de = ds + relativedelta(months=interv, days=-1)

                if de.strftime('%Y-%m-%d') > fy.date_stop:
                    de = datetime.strptime(fy.date_stop, '%Y-%m-%d')

                period_obj.create({
                    'name': ds.strftime('%m/%Y'),
                    'code': ds.strftime('%m/%Y'),
                    'date_start': ds.strftime('%Y-%m-%d'),
                    'date_stop': de.strftime('%Y-%m-%d'),
                    'fiscalyear_id': fy.id,
                })
                ds = ds + relativedelta(months=interv)
            period_obj.create({
                    'name':  "%s %s" % ('Closing Period', de.strftime('%Y')),
                    'code': "%s/%s" % ((de.month + 1), de.strftime('%Y')),
                    'date_start': de,
                    'date_stop': de,
                    'special': True,
                    'fiscalyear_id': fy.id,
                })
        return True


class AccountPeriod(models.Model):
    _name = "account.period"
    _description = "Account period"

    name = fields.Char('Nombre', required=True)
    code = fields.Char(u'Código', size=12)
    special = fields.Boolean('Opening/Closing Period',
                             help="These periods can overlap.")
    date_start = fields.Date('Inicio', required=True,
                             states={'done':[('readonly',True)]})
    date_stop = fields.Date('Fin', required=True,
                            states={'done':[('readonly',True)]})
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        u'Año Fiscal',
        required=True,
        states={'done':[('readonly',True)]},
        ondelete='cascade',
    )
    state = fields.Selection(
        [('draft','Open'), ('done','Closed')],
        'Estado',
        readonly=True,
        copy=False,
        default='draft',
        help="""When monthly periods are created. The status is \'Draft\'.
            At the end of monthly period it is in \'Done\' status."""
    )
    company_id = fields.Integer(
        related='fiscalyear_id.company_id.id',
        string='Company',
        store=True,
        readonly=True
    )

    _order = "date_start, special desc"
    _sql_constraints = [
        ('name_company_uniq', 'unique(name, company_id)', 'The name of the period must be unique per company!'),
    ]

    @api.returns('self')
    def find(self, dt=None, context=None):
        if context is None: context = {}
        if not dt:
            dt = fields.Date.context_today(self)
        args = [('date_start', '<=' ,dt), ('date_stop', '>=', dt)]
        if context.get('company_id', False):
            args.append(('company_id', '=', context['company_id']))
        else:
            company_id = self.env.user.company_id.id
            args.append(('company_id', '=', company_id))
        result = []
        #if context.get('account_period_prefer_normal', True):
            ## look for non-special periods first, and fallback to all if no result is found
            #result = self.search([('special', '=', False)])
            #print 'context'
            #print result
        if not result:
            result = self.search(args)
        if not result:
            model, action_id = self.env['ir.model.data'].get_object_reference('account', 'action_account_period')
            msg = _('There is no period defined for this date: %s.\nPlease go to Configuration/Periods.') % dt
            raise openerp.exceptions.RedirectWarning(msg, action_id, _('Go to the configuration panel'))
        return result


class AccountJournalPeriod(models.Model):
    _name = "account.journal.period"
    _description = "Journal Period"

    name = fields.Char('Nombre', required=True)
    journal_id = fields.Many2one('account.journal', 'Journal', required=True,
                                 ondelete="cascade")
    period_id = fields.Many2one('account.period', 'Period', required=True,
                                ondelete="cascade")
    #icon = fields.function(_icon_get, string='Icon', type='char')
    active = fields.Boolean(
        'Active',
        help="""If the active field is set to False, it will allow you to hide
        the journal period without removing it."""
    )
    state = fields.Selection(
        [('draft','Draft'), ('printed','Printed'), ('done','Done')],
        'Status',
        required=True,
        readonly=True,
        help="""When journal period is created. The status is \'Draft\'.
        If a report is printed it comes to \'Printed\' status.
        When all transactions are done, it comes in \'Done\' status."""
    )
    #fiscalyear_id = fields.Many2one(
        #'account.fiscalyear',
        #related='period_id.fiscalyear_id'
    #)
    #company_id = fields.Integer(
        #related='period_id.company_id.id',
        #string='Company',
        #store=True,
        #readonly=True
    #)