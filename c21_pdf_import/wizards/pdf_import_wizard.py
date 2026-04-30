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


