# Copyright 2017 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
logger = logging.getLogger(__name__)


def _add_is_private_column(cr):
    cr.execute("""SELECT column_name
    FROM information_schema.columns
    WHERE table_name='medical_quote' AND
    column_name='is_private'""")
    if not cr.fetchone():
        cr.execute(
            """
            ALTER TABLE medical_quote ADD COLUMN is_private boolean;
            COMMENT ON COLUMN medical_quote.is_private IS 'Is private';
            """)
        logger.info('Created column is_private of medical_quote')


def _add_price_column(cr):
    cr.execute("""SELECT column_name
    FROM information_schema.columns
    WHERE table_name='medical_quote_line' AND
    column_name='price'""")
    if not cr.fetchone():
        cr.execute(
            """
            ALTER TABLE medical_quote_line ADD COLUMN price float;
            COMMENT ON COLUMN medical_quote_line.price IS 'Price';
            """)
        logger.info('Created column price of medical_quote_line')


def _add_amount_column(cr):
    cr.execute("""SELECT column_name
    FROM information_schema.columns
    WHERE table_name='medical_quote_line' AND
    column_name='amount'""")
    if not cr.fetchone():
        cr.execute(
            """
            ALTER TABLE medical_quote_line ADD COLUMN amount float;
            COMMENT ON COLUMN medical_quote_line.amount IS 'Amount';
            """)
        logger.info('Created column amount of medical_quote_line')


def _update_is_private(cr):
    # Update is_private flag
    cr.execute("""
            UPDATE medical_quote
            SET is_private = True
            WHERE id NOT IN (
                SELECT DISTINCT quote_id
                FROM medical_quote_line
                WHERE coverage_price > 0.0)
        """)
    logger.info('Updated private flag')


def _update_amount_price(cr):
    # Update amount and price
    cr.execute("""
        UPDATE medical_quote_line
        SET price = coverage_price,
            amount = coverage_price * quantity
        FROM medical_quote as mq
        WHERE mq.is_private = False
    """)
    cr.execute("""
        UPDATE medical_quote_line
        SET price = private_price,
            amount = private_price * quantity
        FROM medical_quote as mq
        WHERE mq.is_private = True
    """)
    logger.info('Updated price and amount in medical_quote_line')


def migrate(cr, version):
    if not version:
        return
    logger.info('Start of cb_medical_quote migration')
    _add_is_private_column(cr)
    _add_price_column(cr)
    _add_amount_column(cr)
    _update_is_private(cr)
    _update_amount_price(cr)
    logger.info('End of of cb_medical_quote migration')
