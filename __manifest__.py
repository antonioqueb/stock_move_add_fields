{
    'name': 'Stock Move Customization for Product Rolls with Unique Properties',
    'version': '1.0.0',
    'category': 'Stock',
    'summary': 'Adds custom fields like Gramaje, Ancho, Tipo, Kilos, and Planta to stock move operations, specifically for product rolls with unique properties.',
    'description': """
        Stock Move Customization for Product Rolls with Unique Properties
        ==================================================================
        Developed by Alphaqueb Consulting S.A.S., this module enhances the stock and inventory management capabilities in Odoo by introducing custom fields specific to products such as rolls (e.g., paper rolls, textile rolls, etc.) with unique attributes. The new fields include Gramaje, Ancho, Tipo, Kilos, Planta, and Folio, allowing for more accurate tracking of individual rolls within the same product category.

        Key Features:
        -------------
        - Custom fields added to stock moves: Gramaje, Ancho, Tipo, Kilos, Planta, and Folio.
        - Tailored for industries dealing with products like rolls that have distinct attributes.
        - Seamlessly integrates with Odoo's native stock and inventory operations, providing enhanced control and precision.

        License and Usage:
        ------------------
        This module is provided by Alphaqueb Consulting S.A.S. and is licensed under a commercial license. Its usage is restricted to authorized entities in accordance with the terms outlined in the licensing agreement. Unauthorized distribution or reproduction of this module is prohibited.

        Author: Alphaqueb Consulting S.A.S.
        Support: info@alphaquebconsulting.online
        License: Commercial License - Authorized Use Only
    """,
    'author': 'Alphaqueb Consulting S.A.S.',
    'website': 'https://www.alphaquebconsulting.online',
    'license': 'OPL-1',
    'maintainer': 'Alphaqueb Consulting S.A.S.',
    'depends': ['stock'],
    'data': [
        'views/stock_picking_view.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
