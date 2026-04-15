# -*- coding: utf-8 -*-
from odoo import models, fields, api


class C21AdminChangelog(models.Model):
    _name = 'c21.admin.changelog'
    _description = 'C21 Admin Changelog'
    _order = 'date desc, id desc'

    date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.context_today,
    )
    description = fields.Text(
        string='Description',
        required=True,
    )
    module_name = fields.Char(
        string='Module',
        default='c21_property_listing',
    )
    change_type = fields.Selection([
        ('feature', 'New Feature'),
        ('fix', 'Bug Fix'),
        ('improvement', 'Improvement'),
        ('config', 'Configuration'),
        ('data', 'Data Change'),
        ('other', 'Other'),
    ], string='Type', default='feature')
    author = fields.Char(string='Author')

    def name_get(self):
        result = []
        for record in self:
            name = f"{record.date} - {record.description[:50]}"
            result.append((record.id, name))
        return result
