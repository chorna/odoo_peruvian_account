{
    'name': 'Peruvian Account',
    'author': 'chorna',
    'version': '1.0',
    'category': 'Account',
    'description': """
        Contabilidad Peruana
    """,
    'depends': ['account',],
    'data': [
        'views/partner.xml',
        'views/period.xml',
        'views/close_period.xml',
        
        'wizard/account_fiscalyear_close_state.xml',
        'wizard/account_period_close_view.xml',
        
        'views/menu.xml',
        'views/account_invoice.xml',
        
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
