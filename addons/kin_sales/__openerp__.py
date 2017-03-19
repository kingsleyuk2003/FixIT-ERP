{
    'name': 'Sales Modifications',
    'version': '0.1',
    'category': 'Sales',
    'description': """
Sales Modifications.
=======================================================================================
""",
    'author': 'Kingsley',
    'website': 'http://kinsolve.com',
    'depends': ['base','sale','account','sale_margin','sales_team','sale_stock','purchase_request'],
    'data': [
        'sale_view.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'mail_template.xml',
        'sequence.xml',
    ],
    'test':[],
    'installable': True,
    'images': [],
}