# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Medical Sale Invoice Group Method',
    'version': '11.0.1.0.0',
    'author': 'Eficent, Creu Blanca, Odoo Community Association (OCA)',
    'category': 'Medical',
    'depends': [
        'medical_base',
        'cb_medical_financial_coverage_agreement',
        'sale',
        'barcodes',
        'sale_invoice_group_method',
        'medical_administration_encounter',
        'sale_merge_draft_invoice',
    ],
    'data': [
        'data/medical_preinvoice_group_sequence.xml',
        'data/medical_invoice_group.xml',
        'security/ir.model.access.csv',
        'views/medical_preinvoice_group_line_view.xml',
        'views/sale_order_view.xml',
        'views/medical_preinvoice_group_views.xml',
        'views/medical_sale_invoice_group_method_menu.xml',
        'views/medical_coverage_agreement_view.xml',
        'wizard/invoice_sales_by_group_view.xml',
    ],
    'website': 'https://github.com/OCA/vertical-medical',
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
}
