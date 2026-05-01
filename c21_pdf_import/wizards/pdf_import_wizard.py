import requests
import base64
import logging
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class PdfImportWizard(models.TransientModel):
    _name = 'c21.pdf.import.wizard'
    _description = 'PDF Import Wizard'

    # File upload
    pdf_file = fields.Binary(string='PDF File', attachment=False, required=True)
    pdf_filename = fields.Char(string='Filename')

    notes = fields.Text(string='Notes', help='Optional notes for this import')

    # Config - can be set in System Parameters
    webhook_url = fields.Char(
        string='n8n Webhook URL',
        default=lambda self: self.env['ir.config_parameter'].sudo().get_param(
            'c21.n8n_onedrive_upload_webhook', ''
        ),
        help='Webhook URL for uploading PDF to OneDrive'
    )

    def action_trigger_import(self):
        """Upload PDF to OneDrive via n8n webhook, which triggers the processing workflow"""
        self.ensure_one()

        webhook_url = self.webhook_url or self.env['ir.config_parameter'].sudo().get_param(
            'c21.n8n_onedrive_upload_webhook', ''
        )

        if not webhook_url:
            raise UserError(
                'n8n Webhook URL not configured.\n\n'
                'Please set it in:\n'
                'Settings → Technical → System Parameters\n'
                'Key: c21.n8n_onedrive_upload_webhook\n'
                'Value: https://your-n8n-instance/webhook/odoo-upload-to-onedrive'
            )

        # Save webhook URL for next time
        if self.webhook_url:
            self.env['ir.config_parameter'].sudo().set_param(
                'c21.n8n_onedrive_upload_webhook', self.webhook_url
            )

        # Validate file
        if not self.pdf_file:
            raise UserError('Please select a PDF file to upload.')
        if not self.pdf_filename or not self.pdf_filename.lower().endswith('.pdf'):
            raise UserError('Please upload a PDF file (.pdf)')

        # Create log entry
        log = self.env['c21.pdf.import.log'].create({
            'name': self.pdf_filename,
            'status': 'pending',
            'triggered_by': self.env.user.id,
            'notes': self.notes,
        })

        # Append log ID to filename so n8n workflow can callback
        # e.g., "招租 - YYR.pdf" -> "招租 - YYR_ODOO123.pdf"
        base_name = self.pdf_filename.rsplit('.', 1)[0]
        upload_filename = f"{base_name}_ODOO{log.id}.pdf"

        try:
            # Prepare payload - send file to OneDrive upload webhook
            payload = {
                'file_name': upload_filename,
                'file_data': self.pdf_file.decode('utf-8'),  # Already base64
                'odoo_log_id': log.id,
                'triggered_by': self.env.user.name,
            }

            file_size = len(base64.b64decode(self.pdf_file))
            _logger.info(f'Uploading PDF to OneDrive: {self.pdf_filename} ({file_size} bytes)')

            response = requests.post(
                webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=120  # Longer timeout for file upload
            )

            if response.status_code == 200:
                result = response.json() if response.text else {}
                if result.get('success'):
                    log.write({
                        'status': 'processing',
                        'notes': (self.notes or '') + f'\nUploaded to OneDrive. Processing will start automatically.',
                    })
                    message = f'PDF uploaded to OneDrive successfully! Processing will start automatically.'
                else:
                    error_msg = result.get('error', 'Unknown error')
                    log.write({
                        'status': 'failed',
                        'error_message': error_msg,
                    })
                    message = f'Upload failed: {error_msg}'
            else:
                log.write({
                    'status': 'failed',
                    'error_message': f'HTTP {response.status_code}: {response.text[:500]}',
                })
                message = f'Upload failed: HTTP {response.status_code}'

        except requests.exceptions.Timeout:
            log.write({
                'status': 'processing',
                'notes': (self.notes or '') + '\n[Upload may still be in progress]',
            })
            message = 'Upload in progress (request timed out but may still complete)'

        except Exception as e:
            _logger.exception('PDF Upload error')
            log.write({
                'status': 'failed',
                'error_message': str(e),
            })
            raise UserError(f'Failed to upload PDF: {e}')

        # Show result and redirect to import history
        return {
            'type': 'ir.actions.act_window',
            'name': 'Import History',
            'res_model': 'c21.pdf.import.log',
            'view_mode': 'list,form',
            'target': 'current',
        }
