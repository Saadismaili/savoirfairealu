# -*- coding: utf-8 -*-

{
    'name': 'custom sale',
    'version': '10.0',
    'description': """
                custom sale
                    """,
    'category': 'Sales Management',
    'author': 'ANDEMA',
    'website': 'http://www.andemaconsulting.com',
    'depends': [
        'sale',
        'product_extend'
    ],
    'data': ['views/sale_views.xml',
             'views/report_saleorder.xml'
    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
}
