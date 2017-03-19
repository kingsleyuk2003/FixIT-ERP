{
    'name': 'Product Modifications',
    'version': '0.1',
    'category': 'product',
    'description': """
Product Modifications
=======================================================================================
""",
    'author': 'Kingsley',
    'website': 'http://kinsolve.com',
    'depends': ['base','product','stock'],
    'data': [
        'cron_data.xml',
        'product.xml',
        'mail_template.xml',
        'security/security.xml',
    ],
    'test':[],
    'installable': True,
    'images': [],
}