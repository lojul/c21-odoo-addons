import json
import logging
from odoo import http, fields
from odoo.http import request

_logger = logging.getLogger(__name__)


class PdfImportController(http.Controller):

    @http.route('/api/pdf-import/callback', type='json', auth='none', methods=['POST'], csrf=False)
    def import_callback(self, **kwargs):
        """Callback endpoint for n8n to update import status"""
        try:
            data = request.jsonrequest
            log_id = data.get('odoo_log_id')
            status = data.get('status')  # 'completed' or 'failed'
            error_message = data.get('error_message', '')
            property_id = data.get('property_id')
            chunks_indexed = data.get('chunks_indexed', 0)
            images_uploaded = data.get('images_uploaded', 0)

            if not log_id:
                return {'success': False, 'error': 'Missing odoo_log_id'}

            # Find and update the log entry
            log = request.env['c21.pdf.import.log'].sudo().browse(int(log_id))
            if not log.exists():
                return {'success': False, 'error': f'Log {log_id} not found'}

            update_vals = {
                'status': status or 'completed',
            }

            if status == 'completed':
                update_vals['complete_date'] = fields.Datetime.now()

            if error_message:
                update_vals['error_message'] = error_message

            if property_id:
                update_vals['property_id'] = int(property_id)

            if chunks_indexed:
                update_vals['chunks_indexed'] = chunks_indexed

            if images_uploaded:
                update_vals['images_uploaded'] = images_uploaded

            log.write(update_vals)
            _logger.info(f'PDF Import callback: Log {log_id} updated to {status}')

            return {'success': True, 'log_id': log_id, 'status': status}

        except Exception as e:
            _logger.exception('PDF Import callback error')
            return {'success': False, 'error': str(e)}
