{
    'name': 'Help Desk',
    'version': '0.1',
    'category': 'Sales',
    'description': """
HelpDesk
=======================================================================================
""",
    'author': 'Kingsley',
    'website': 'http://kinsolve.com',
    'depends': ['base','mail','stock','analytic'],
    'data': [
        'security/helpdesk_security.xml',
        'security/ir.model.access.csv',
        'helpdesk_view.xml',
        'sequence.xml',
        'mail_template.xml',
    ],
    'test':[],
    'installable': True,
    'images': [],
}