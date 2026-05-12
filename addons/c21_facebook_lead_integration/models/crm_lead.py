from odoo import fields, models


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    x_facebook_comment_id = fields.Char(
        string='Facebook Comment ID',
        help='Original Facebook comment ID'
    )
    x_facebook_post_id = fields.Char(
        string='Facebook Post ID',
        help='Facebook post where the comment was made'
    )
    x_lead_source = fields.Selection([
        ('facebook_comment', 'Facebook Comment'),
        ('facebook_ad', 'Facebook Ad'),
        ('facebook_messenger', 'Facebook Messenger'),
        ('instagram_comment', 'Instagram Comment'),
        ('instagram_dm', 'Instagram DM'),
        ('website', 'Website'),
        ('referral', 'Referral'),
        ('manual', 'Manual Entry'),
        ('other', 'Other'),
    ], string='Lead Source', default='manual')
    x_source_url = fields.Char(
        string='Source URL',
        help='URL where the lead originated (comment permalink, ad URL, etc.)'
    )
    x_original_message = fields.Text(
        string='Original Message',
        help='The original comment or message from the lead'
    )
    x_post_context = fields.Text(
        string='Post Context',
        help='Context about the post/ad the lead commented on'
    )
