from odoo import models, fields


class CsvImportLog(models.Model):
    _name = 'c21.csv.import.log'
    _description = 'CSV Import Log'
    _order = 'create_date desc'

    name = fields.Char('File Name', required=True)
    status = fields.Selection([
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('partial', 'Partial'),
        ('failed', 'Failed'),
    ], default='pending', string='Status')

    triggered_by = fields.Many2one(
        'res.users', string='Imported By',
        default=lambda self: self.env.user)
    import_date = fields.Datetime(
        'Import Date', default=fields.Datetime.now)

    total_rows = fields.Integer('Total Rows')
    success_count = fields.Integer('Imported')
    error_count = fields.Integer('Errors')

    property_ids = fields.Many2many(
        'c21.property.listing', 'c21_csv_import_log_property_rel',
        'log_id', 'property_id', string='Created Properties')
    error_details = fields.Text('Error Details')

    def action_view_properties(self):
        """Open list of created properties."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Imported Properties',
            'res_model': 'c21.property.listing',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.property_ids.ids)],
        }

    def action_back_to_list(self):
        """Go back to Import History list."""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Import History (CSV)',
            'res_model': 'c21.csv.import.log',
            'view_mode': 'list,form',
            'target': 'current',
        }
