.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
   :target: https://www.gnu.org/licenses/lgpl-3.0-standalone.html
   :alt: License: LGPL-3

==================
Medical Commission
==================

This module allows you to define fixed or variable fees on medical
services through actions. Commissions can be changed on Procedure Requests or
Procedures.

It also adds the commission agent field to practitioners in order to settle
the commissions to that agent once the service has been provided.

Installation
============

To install this module, simply follow the standard install process.

Usage
=====

Define service's fee
--------------------

#. Go to Medical / Workflow / Activity definition
#. Click on Resource Product and activate the boolean 'Medical Commissions'
#. Go to an action with that activity definition and specify the fixed or
   the variable fee for that service.

Add commission agent to a practitioner
--------------------------------------

#. Go to Sales / Commissions Management / Agents
#. Remove the filter 'Agents'
#. Search or create a partner that has to be the agent. Inside the partner
   view form, go to the 'Sales & Purchases' page and activate the flag 'Agent'
#. Go to Medical / Practitioners
#. Select the practitioner and inside the 'Commission Agents page' select the
   agent(s) for that practitioner.

Create a Procedure
------------------

#. Generate a Procedure with that service
#. Select the practitioner and if the practitioner only has one agent it is
   automatically set as Commission Agent in the page 'Commission Agent' in
   the form view. If more than one, select one from the given options.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/159/11.0

Known Issues / Roadmap
======================

* The python files `sale_order.py`, `sale_order_line.py` and `account_invoice.py`
  can't be tested at the moment. They are pending to review when the module
  `careplan_sale` is ready.

Bug Tracker
===========

Bugs are tracked on
`GitHub Issues <https://github.com/OCA/vertical-medical/issues>`_. In case of
trouble, please check there if your issue has already been reported. If you
spotted it first, help us smash it by providing detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association:
  `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Jordi Ballester <jordi.ballester@eficent.com>
* Roser Garcia <roser.garcia@eficent.com>
* Enric Tobella <etobella@creublanca.es>


Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
