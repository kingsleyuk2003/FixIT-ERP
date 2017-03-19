{
    'name': 'Common Reports Modifications',
    'version': '0.1',
    'category': 'report',
    'description': """
Report Modifications
=======================================================================================
""",
    'author': 'Kingsley',
    'website': 'http://kinsolve.com',
    'depends': ['base','sale','kin_sales','purchase','kin_purchase','account','kin_account','stock','kin_stock','report_xlsx'],
    'data': [
        'wizard/stock_level_wizard_view.xml',
        'report/custom_report_layouts.xml',
        'report/custom_rfq.xml',
        'report/custom_purchase_order.xml',
        'report/custom_sales_quotation.xml',
        'report/custom_sales_order.xml',
        'report/custom_waybill.xml',
        'report/custom_invoice.xml',
        'kin_report.xml',
    ],
    'test':[],
    'installable': True,
    'images': [],
}