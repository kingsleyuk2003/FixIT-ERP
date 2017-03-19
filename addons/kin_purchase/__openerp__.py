{
    'name': 'Purchase Modifications',
    'version': '0.1',
    'category': 'Purchase',
    'description': """
Purchase Modifications
=======================================================================================
""",
    'author': 'Kingsley',
    'website': 'http://kinsolve.com',
    'depends': ['base','purchase','purchase_request'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'purchase_view.xml',
        'mail_template.xml',
        'report/report_purchasequotation.xml',
        'report/report_purchaseorder.xml',
        'sequence.xml',
    ],
    'test':[],
    'installable': True,
    'images': [],
}