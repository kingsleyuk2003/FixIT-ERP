{
    'name': 'Sale Double Validation',
    'version': '0.1',
    'category': 'Sales',
    'description': """
Sales Double Validation
=======================================================================================
""",
    'author': 'Kingsley',
    'website': 'http://kinsolve.com',
    'depends': ['base','sale','account','kin_sales'],
    'data': [
        'security/security.xml',
        'wizard/sales_orders_confirm.xml',
        'wizard/sales_order_disapprove.xml',
        'sale_view.xml',
        'mail_template.xml',
    ],
    'test':[],
    'installable': True,
    'images': [],
}