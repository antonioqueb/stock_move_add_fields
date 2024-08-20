{
    'name': 'Stock Move Customization - Gramaje',
    'version': '1.0',
    'category': 'Stock',
    'summary': 'Add Gramaje, Ancho, Tipo, Kilos, and Planta fields to Stock Move',
    'depends': ['stock'],
    'data': [
        'views/stock_picking_view.xml',  # Modificaciones de la vista de picking
        'report/stock_label_report.xml',  # Reporte QWeb para las etiquetas
    ],
    'installable': True,
    'application': False,
}
