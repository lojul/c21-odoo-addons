import requests
import logging
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class PdfImportWizard(models.TransientModel):
    _name = 'c21.pdf.import.wizard'
    _description = 'PDF Import Wizard'

    action_type = fields.Selection([
        ('process_folder', 'Process OneDrive Folder'),
    ], string='Action', default='process_folder', required=True)

    notes = fields.Text(string='Notes', help='Optional notes for this import')

    # Config - can be set in System Parameters
    webhook_url = fields.Char(
        string='n8n Webhook URL',
        default=lambda self: self.env['ir.config_parameter'].sudo().get_param(
            'c21.n8n_pdf_import_webhook', ''
        )
    )

    def action_trigger_import(self):
        """Trigger the n8n PDF import workflow"""
        self.ensure_one()

        webhook_url = self.webhook_url or self.env['ir.config_parameter'].sudo().get_param(
            'c21.n8n_pdf_import_webhook', ''
        )

        if not webhook_url:
            raise UserError(
                'n8n Webhook URL not configured.\n\n'
                'Please set it in:\n'
                'Settings → Technical → System Parameters\n'
                'Key: c21.n8n_pdf_import_webhook\n'
                'Value: https://your-n8n-instance/webhook/xxx'
            )

        # Create log entry
        log = self.env['c21.pdf.import.log'].create({
            'name': f'Manual Import - {fields.Datetime.now()}',
            'status': 'pending',
            'triggered_by': self.env.user.id,
            'notes': self.notes,
        })

        try:
            # Call n8n webhook
            _logger.info(f'Triggering n8n PDF import webhook: {webhook_url}')

            response = requests.post(
                webhook_url,
                json={
                    'action': self.action_type,
                    'triggered_by': self.env.user.name,
                    'odoo_log_id': log.id,
                    'callback_url': self._get_callback_url(),
                },
                headers={'Content-Type': 'application/json'},
                timeout=30
            )

            if response.status_code == 200:
                result = response.json() if response.text else {}
                log.write({
                    'status': 'processing',
                    'n8n_execution_id': result.get('executionId', ''),
                })
                message = 'Import triggered successfully! Check Import History for status.'
            else:
                log.write({
                    'status': 'failed',
                    'error_message': f'HTTP {response.status_code}: {response.text[:500]}',
                })
                message = f'Import failed: HTTP {response.status_code}'

        except requests.exceptions.Timeout:
            log.write({
                'status': 'processing',
                'notes': (self.notes or '') + '\n[Webhook timeout - workflow may still be running]',
            })
            message = 'Import triggered (webhook timed out, but workflow may still be running)'

        except Exception as e:
            _logger.exception('PDF Import webhook error')
            log.write({
                'status': 'failed',
                'error_message': str(e),
            })
            raise UserError(f'Failed to trigger import: {e}')

        # Show result
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'PDF Import',
                'message': message,
                'type': 'success' if 'successfully' in message else 'warning',
                'sticky': False,
                'next': {
                    'type': 'ir.actions.act_window',
                    'res_model': 'c21.pdf.import.log',
                    'view_mode': 'list,form',
                    'target': 'current',
                },
            },
        }

    def _get_callback_url(self):
        """Get callback URL for n8n to update import status"""
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', '')
        return f'{base_url}/api/pdf-import/callback' if base_url else ''


class PdfImportCallback(models.Model):
    """Handle callbacks from n8n workflow"""
    _name = 'c21.pdf.import.callback'
    _description = 'PDF Import Callback Handler'
    _auto = False  # No database table

    @api.model
    def process_callback(self, data):
        """
        Process callback from n8n workflow.
        Called via JSON-RPC or custom controller.

        Expected data:
        {
            'odoo_log_id': int,
            'status': 'completed' | 'failed',
            'property_id': int (optional),
            'chunks_indexed': int,
            'images_uploaded': int,
            'error_message': str (optional),
        }
        """
        log_id = data.get('odoo_log_id')
        if not log_id:
            return {'success': False, 'error': 'Missing odoo_log_id'}

        log = self.env['c21.pdf.import.log'].sudo().browse(log_id)
        if not log.exists():
            return {'success': False, 'error': f'Log {log_id} not found'}

        update_vals = {
            'status': data.get('status', 'completed'),
            'complete_date': fields.Datetime.now(),
            'chunks_indexed': data.get('chunks_indexed', 0),
            'images_uploaded': data.get('images_uploaded', 0),
        }

        if data.get('property_id'):
            update_vals['property_id'] = data['property_id']

        if data.get('error_message'):
            update_vals['error_message'] = data['error_message']

        if data.get('file_name'):
            update_vals['name'] = data['file_name']

        log.write(update_vals)

        return {'success': True, 'log_id': log_id}
