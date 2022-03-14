# -*- coding: utf-8 -*-
{
    'name': "Templates Customer",

    'summary': """
        Cutom templates reports""",

    'description': """
        Cutom templates reports
    """,

    'author': "Osisoftware",
    'website': "http://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/sale_template.xml',
        'views/invoice_template.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
