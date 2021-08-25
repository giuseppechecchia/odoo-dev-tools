# -*- coding: utf-8 -*-
{
    'name': 'Developer Tools',
    'summary': 'A little suite of tools to simplify @chrisbiava life',
    'description': """
        A little suite of tools to simplify @chrisbiava life.
        Originally writed in minutes for frmoda.com
    """,
    'author': 'Giuseppe Checchia',
    'website': 'https://github.com/giuseppechecchia',
    'category': 'Utility',
    'sequence': 100,
    'version': '0.2',
    'depends': [
            'base',
            'queue_job',
    ],
    'data': [
        'scheduler/dev_data.xml',
        # 'security/ir.model.access.csv'
    ],
    'external_dependencies': {
        'python': [
            'unittest',
            'responses',
            'requests',
        ],
    },
    'auto_install': False,
    'application': False,
    'installable': True
}
