import requests
import base64
import logging
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class PdfImportWizard(models.TransientModel):
    _name = 'c21.pdf.import.wizard'
    _description = 'PDF Import Wizard'

    action_type = fields.Selection([
        ('upload_file', 'Upload PDF File'),
        ('process_folder', 'Process OneDrive Folder'),
    ], string='Action', default='upload_file', required=True)

    # File upload
    pdf_file = fields.Binary(string='PDF File', attachment=False)
    pdf_filename = fields.Char(string='Filename')

    notes = fields.Text(string='Notes', help='Optional notes for this import')

    # Config - can be set in System Parameters
    webhook_url = fields.Char(
        string='n8n Webhook URL',
        default=lambda self: self.env['ir.config_parameter'].sudo().get_param(
            'c21.n8n_pdf_import_webhook', ''
        )
    )

    @api.onchange('action_type')
    def _onchange_action_type(self):
        if self.action_type == 'process_folder':
            self.pdf_file = False
            self.pdf_filename = False

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

        # Validate file upload if selected
        if self.action_type == 'upload_file':
            if not self.pdf_file:
                raise UserError('Please select a PDF file to upload.')
            if not self.pdf_filename or not self.pdf_filename.lower().endswith('.pdf'):
                raise UserError('Please upload a PDF file (.pdf)')

        # Create log entry
        log_name = self.pdf_filename if self.pdf_file else f'Folder Import - {fields.Datetime.now()}'
        log = self.env['c21.pdf.import.log'].create({
            'name': log_name,
            'status': 'pending',
            'triggered_by': self.env.user.id,
            'notes': self.notes,
        })

        try:
            # Prepare payload
            payload = {
                'action': self.action_type,
                'triggered_by': self.env.user.name,
                'odoo_log_id': log.id,
            }

            # Add file data if uploading
            if self.action_type == 'upload_file' and self.pdf_file:
                payload['file_name'] = self.pdf_filename
                payload['file_data'] = self.pdf_file.decode('utf-8')  # Already base64
                payload['file_size'] = len(base64.b64decode(self.pdf_file))

            _logger.info(f'Triggering n8n PDF import webhook: {webhook_url}')
            _logger.info(f'Action: {self.action_type}, File: {self.pdf_filename or "N/A"}')

            response = requests.post(
                webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=60  # Longer timeout for file upload
            )

            if response.status_code == 200:
                result = response.json() if response.text else {}
                log.write({
                    'status': 'processing',
                    'n8n_execution_id': result.get('executionId', ''),
                })
                message = f'Import triggered successfully! File: {self.pdf_filename or "Folder scan"}'
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


