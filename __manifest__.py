{
    'name': 'Stock Move Customization - Gramaje',
    'version': '1.0',
    'category': 'Stock',
    'summary': 'Add Gramaje field to Stock Move',
    'depends': ['stock'],  # Dependencia del módulo stock
    'data': [
        'views/stock_picking_view.xml',  # Archivo que modifica la vista de picking
    ],
    'installable': True,
    'application': False,
}
