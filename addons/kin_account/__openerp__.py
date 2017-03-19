{
    'name': 'Account Modifications',
    'version': '0.1',
    'category': 'Accounting',
    'description': """
Account Modifications
=======================================================================================
""",
    'author': 'Kingsley',
    'website': 'http://kinsolve.com',
    'depends': ['base','account','account_asset','purchase','account_extra_reports','analytic','report'],
    'data': [
        'account_view.xml',
        'account_invoice_view.xml',
        'product_view.xml',
        'wizard/account_report_partner_ledger_view.xml',
        'wizard/account_report_general_ledger_view.xml',
        'wizard/account_report_aged_partner_balance_view.xml',
        'report/report_trialbalance.xml',
        'report/account_invoice.xml',
    ],
    'test':[],
    'installable': True,
    'images': [],
}