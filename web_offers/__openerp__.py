# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo Module
#    Copyright (C) 2015 Grover Menacho (<http://www.grovermenacho.com>).
#    Autor: Grover Menacho
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Web Offers',
    'version': '1.0',
    'category': 'Tools',
    'summary': 'Web Offers',
    'description': """
Base URL Connector    """,
    'author': 'Grover Menacho',
    'website': 'http://www.grovermenacho.com',
    'depends': ['web','base', 'base_url_connector','sale','sales_team','sale_contract'],
    'data': ['web_offers_view.xml',
             'product_view.xml',
             'crm_team_view.xml',
             'crm_brand_view.xml',
             'crm_site_view.xml',
             'web_affiliates_view.xml',
             'account_payment_view.xml',
             'sale_view.xml',
             'ir_cron.xml',
             'wizard/update_offers_wizard.xml',
             'report/customer_biller_lp_report_view.xml',
             #'account_voucher_view.xml',
             'security/ir.model.access.csv',
             'subscription_menu.xml',
             'report/subscription_reports_view.xml',
             'reports_dashboard.xml'],
    'qweb': [],
    'installable': True,
    'active': False,
    'application': True,
}