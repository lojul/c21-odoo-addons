from odoo import models, fields, api


class PdfImportLog(models.Model):
    _name = 'c21.pdf.import.log'
    _description = 'PDF Import Log'
    _order = 'create_date desc'

    name = fields.Char(string='File Name', required=True)
    status = fields.Selection([
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ], string='Status', default='pending', required=True)

    triggered_by = fields.Many2one('res.users', string='Triggered By',
                                    default=lambda self: self.env.user)
    trigger_date = fields.Datetime(string='Triggered At', default=fields.Datetime.now)
    complete_date = fields.Datetime(string='Completed At')

    property_id = fields.Many2one('c21.property.listing', string='Created/Updated Listing',
                                   ondelete='set null')

    n8n_execution_id = fields.Char(string='n8n Execution ID')
    error_message = fields.Text(string='Error Message')

    # Stats from n8n
    chunks_indexed = fields.Integer(string='Chunks Indexed', default=0)
    images_uploaded = fields.Integer(string='Images Uploaded', default=0)

    notes = fields.Text(string='Notes')

    def action_view_property(self):
        """Open the related property listing"""
        self.ensure_one()
        if self.property_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'c21.property.listing',
                'res_id': self.property_id.id,
                'view_mode': 'form',
                'target': 'current',
            }
        return False
