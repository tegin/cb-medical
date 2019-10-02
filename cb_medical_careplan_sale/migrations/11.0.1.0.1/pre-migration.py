def migrate(cr, version):
    cr.execute(
        "CREATE TABLE invoice_group_method (LIKE "
        "sale_invoice_group_method including all);"
    )
    cr.execute(
        "INSERT INTO invoice_group_method SELECT * FROM "
        "sale_invoice_group_method;"
    )
    cr.execute(
        "UPDATE ir_model_data SET model = 'invoice.group.method' "
        "WHERE model = 'sale.invoice.group.method';"
    )

    cr.execute("SELECT nextval('sale_invoice_group_method_id_seq')")
    next_seq = 1
    for val in cr.fetchone():
        next_seq = val
    cr.execute(
        "CREATE SEQUENCE invoice_group_method_id_seq " "INCREMENT 1 START %s;",
        (next_seq,),
    )
