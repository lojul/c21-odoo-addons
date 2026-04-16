from odoo import models, fields, api
import base64
import requests
import logging

_logger = logging.getLogger(__name__)


class C21PropertyImage(models.Model):
    _name = 'c21.property.image'
    _description = 'Property Image'
    _order = 'sequence, id'

    property_id = fields.Many2one(
        'c21.property.listing', string='Property',
        required=True, ondelete='cascade', index=True)
    name = fields.Char('Description / 描述', help='Image description or alt text')

    # Image storage fields
    image = fields.Image('Image / 圖片', max_width=1920, max_height=1920, required=True)
    image_medium = fields.Image('Medium Image', related='image', max_width=512, max_height=512, store=True)
    image_small = fields.Image('Small Image', related='image', max_width=256, max_height=256, store=True)

    # Legacy URL fields (kept for migration purposes)
    image_url = fields.Char('Image URL / 圖片網址 (Legacy)', help='Legacy field - use for importing from URL')
    thumbnail_url = fields.Char('Thumbnail URL / 縮圖網址 (Legacy)', help='Legacy field')

    sequence = fields.Integer('Sequence / 排序', default=10)
    is_cover = fields.Boolean('Is Cover Image / 是否封面圖', default=False)

    @api.model_create_multi
    def create(self, vals_list):
        """Download image from URL if image_url is provided but image is not"""
        for vals in vals_list:
            if vals.get('image_url') and not vals.get('image'):
                try:
                    image_data = self._download_image_from_url(vals['image_url'])
                    if image_data:
                        vals['image'] = image_data
                        _logger.info(f"Downloaded image from URL: {vals['image_url']}")
                except Exception as e:
                    _logger.warning(f"Failed to download image from {vals.get('image_url')}: {str(e)}")
        return super().create(vals_list)

    def write(self, vals):
        """Download image from URL if image_url is updated but image is not"""
        if vals.get('image_url') and not vals.get('image'):
            try:
                image_data = self._download_image_from_url(vals['image_url'])
                if image_data:
                    vals['image'] = image_data
                    _logger.info(f"Downloaded image from URL: {vals['image_url']}")
            except Exception as e:
                _logger.warning(f"Failed to download image from {vals.get('image_url')}: {str(e)}")
        return super().write(vals)

    def _download_image_from_url(self, url):
        """Download image from URL and return base64 encoded data"""
        if not url:
            return False
        try:
            response = requests.get(url, timeout=10, stream=True)
            response.raise_for_status()
            return base64.b64encode(response.content)
        except Exception as e:
            _logger.error(f"Error downloading image from {url}: {str(e)}")
            return False

    def action_download_from_url(self):
        """Action to manually download/refresh image from URL"""
        for record in self:
            if record.image_url:
                image_data = record._download_image_from_url(record.image_url)
                if image_data:
                    record.image = image_data
                    _logger.info(f"Refreshed image for {record.name or record.id} from URL")
        return True
