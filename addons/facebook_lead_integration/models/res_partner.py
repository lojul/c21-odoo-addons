from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    x_facebook_id = fields.Char(
        string='Facebook ID',
        index=True,
        help='Facebook User ID for duplicate detection'
    )
    x_facebook_profile_url = fields.Char(
        string='Facebook Profile',
        help='Link to Facebook profile'
    )
    x_lead_source = fields.Selection([
        ('facebook_comment', 'Facebook Comment'),
        ('facebook_ad', 'Facebook Ad'),
        ('facebook_messenger', 'Facebook Messenger'),
        ('instagram_comment', 'Instagram Comment'),
        ('instagram_dm', 'Instagram DM'),
        ('manual', 'Manual Entry'),
        ('other', 'Other'),
    ], string='Lead Source', default='manual')
    x_source_post_url = fields.Char(
        string='Source Post URL',
        help='URL of the post/ad where the lead originated'
    )
