from odoo import models, fields, api


# District selection for Hong Kong
DISTRICT_SELECTION = [
    # Hong Kong Island
    ('central', 'Central (中環)'),
    ('admiralty', 'Admiralty (金鐘)'),
    ('wan_chai', 'Wan Chai (灣仔)'),
    ('causeway_bay', 'Causeway Bay (銅鑼灣)'),
    ('north_point', 'North Point (北角)'),
    ('quarry_bay', 'Quarry Bay (鰂魚涌)'),
    ('taikoo', 'Taikoo (太古)'),
    ('wong_chuk_hang', 'Wong Chuk Hang (黃竹坑)'),
    ('sheung_wan', 'Sheung Wan (上環)'),
    # Kowloon
    ('tsim_sha_tsui', 'Tsim Sha Tsui (尖沙咀)'),
    ('jordan', 'Jordan (佐敦)'),
    ('mong_kok', 'Mong Kok (旺角)'),
    ('kowloon_bay', 'Kowloon Bay (九龍灣)'),
    ('kwun_tong', 'Kwun Tong (觀塘)'),
    ('san_po_kong', 'San Po Kong (新蒲崗)'),
    # New Territories
    ('kwai_chung', 'Kwai Chung (葵涌)'),
    ('tsuen_wan', 'Tsuen Wan (荃灣)'),
    ('sha_tin', 'Sha Tin (沙田)'),
    ('fo_tan', 'Fo Tan (火炭)'),
    ('tuen_mun', 'Tuen Mun (屯門)'),
    ('yuen_long', 'Yuen Long (元朗)'),
    # Other
    ('other', 'Other (其他)'),
]


class C21PropertyListing(models.Model):
    _name = 'c21.property.listing'
    _description = 'Property Listing'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    # === Identification ===
    ref_code = fields.Char(
        'Reference Code / 參考編號', required=True, index=True, tracking=True,
        help='Unique reference code (e.g., C0000063 for co-working, LS-0001 for leasing)')
    name = fields.Char('Name (English) / 名稱（英文）', required=True, tracking=True)
    name_cn = fields.Char('Name (Chinese) / 名稱（中文）', tracking=True)
    listing_type = fields.Selection([
        ('coworking', 'Co-working Space'),
        ('leasing', 'Leasing Property'),
    ], string='Listing Type / 物業類型', required=True, default='leasing', tracking=True)

    # === Location ===
    district = fields.Selection(
        DISTRICT_SELECTION, string='District / 地區', required=True, index=True, tracking=True)
    building_name = fields.Char('Building Name / 大廈名稱')
    address = fields.Text('Address / 地址')
    floor = fields.Char('Floor / 樓層')
    unit = fields.Char('Unit / 單位')
    latitude = fields.Float('Latitude / 緯度', digits=(10, 7))
    longitude = fields.Float('Longitude / 經度', digits=(10, 7))

    # === Status & Workflow ===
    state = fields.Selection([
        ('available', 'Available'),
        ('under_negotiation', 'Under Negotiation'),
        ('leased', 'Leased'),
        ('off_market', 'Off Market'),
    ], string='Status / 狀態', default='available', tracking=True, index=True)

    approval_status = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('published', 'Published'),
        ('rejected', 'Rejected'),
    ], string='Approval Status / 審批狀態', default='draft', tracking=True, index=True)

    available_from = fields.Date('Available From / 可租日期')

    # === Co-working Specific Fields ===
    operator_id = fields.Many2one(
        'res.partner', string='Operator / 營運商',
        domain=[('is_property_operator', '=', True), ('is_company', '=', True)],
        tracking=True)
    capacity = fields.Integer('Total Capacity / 總容量', help='Total people capacity')
    available_capacity = fields.Integer('Available Capacity / 可用容量')
    size = fields.Integer('Size (sqft) / 面積（平方呎）', help='Total size in square feet')
    hot_desk_price = fields.Monetary('Hot Desk Price / 流動工位價格', help='Monthly price for hot desk in HKD')
    dedicated_desk_price = fields.Monetary('Dedicated Desk Price / 固定工位價格', help='Monthly price for dedicated desk in HKD')
    office_price = fields.Monetary('Private Office Price / 私人辦公室價格', help='Monthly starting price for private office in HKD')

    # === Leasing Specific Fields ===
    property_type = fields.Selection([
        ('office', 'Office'),
        ('retail', 'Retail'),
        ('industrial', 'Industrial'),
    ], string='Property Type / 物業用途', tracking=True)

    building_grade = fields.Selection([
        ('grade_a', 'Grade A'),
        ('grade_b', 'Grade B'),
        ('grade_c', 'Grade C'),
    ], string='Building Grade / 大廈級別', tracking=True)

    business_type = fields.Selection([
        ('dining', 'Dining'),
        ('cafe', 'Cafe'),
        ('beauty', 'Beauty'),
        ('retail_shop', 'Retail Shop'),
        ('convenience', 'Convenience Store'),
        ('medical', 'Medical'),
        ('education', 'Education'),
        ('other', 'Other'),
    ], string='Business Type / 業務類型', help='For retail properties')

    gross_area = fields.Float('Gross Area (sqft) / 建築面積（平方呎）', digits=(12, 2))
    net_area = fields.Float('Net Area (sqft) / 實用面積（平方呎）', digits=(12, 2))
    asking_rent = fields.Monetary('Asking Rent / 叫租', help='Monthly asking rent in HKD')
    rent_per_sqft = fields.Float(
        'Rent per Sqft / 每呎租金', digits=(12, 2), compute='_compute_rent_per_sqft', store=True)
    lease_terms = fields.Char('Lease Terms / 租約條款', help='e.g., 2 years minimum')
    year_built = fields.Char('Year Built / 落成年份')
    total_floors = fields.Integer('Total Floors / 總樓層')

    # === Descriptions ===
    description = fields.Html('Description (English) / 描述（英文）')
    description_cn = fields.Html('Description (Chinese) / 描述（中文）')

    # === Relations ===
    image_ids = fields.One2many('c21.property.image', 'property_id', string='Images / 圖片')
    amenity_ids = fields.Many2many(
        'c21.property.amenity', 'c21_property_listing_amenity_rel',
        'property_id', 'amenity_id', string='Amenities / 設施')
    contact_ids = fields.One2many('c21.property.contact', 'property_id', string='Contacts / 聯絡人')
    currency_id = fields.Many2one(
        'res.currency', string='Currency / 貨幣',
        default=lambda self: self.env.company.currency_id)

    # === Computed Fields ===
    image_count = fields.Integer('Image Count / 圖片數量', compute='_compute_image_count')
    contact_count = fields.Integer('Contact Count / 聯絡人數量', compute='_compute_contact_count')
    display_price = fields.Char('Display Price / 顯示價格', compute='_compute_display_price')

    _ref_code_unique = models.Constraint(
        'UNIQUE(ref_code)',
        'Reference code must be unique!',
    )

    @api.depends('asking_rent', 'net_area')
    def _compute_rent_per_sqft(self):
        for record in self:
            if record.net_area and record.net_area > 0:
                record.rent_per_sqft = record.asking_rent / record.net_area
            else:
                record.rent_per_sqft = 0

    @api.depends('image_ids')
    def _compute_image_count(self):
        for record in self:
            record.image_count = len(record.image_ids)

    @api.depends('contact_ids')
    def _compute_contact_count(self):
        for record in self:
            record.contact_count = len(record.contact_ids)

    @api.depends('listing_type', 'hot_desk_price', 'dedicated_desk_price', 'office_price', 'asking_rent')
    def _compute_display_price(self):
        for record in self:
            if record.listing_type == 'coworking':
                prices = []
                if record.hot_desk_price:
                    prices.append(f"Hot Desk: ${record.hot_desk_price:,.0f}")
                if record.dedicated_desk_price:
                    prices.append(f"Dedicated: ${record.dedicated_desk_price:,.0f}")
                if record.office_price:
                    prices.append(f"Office: ${record.office_price:,.0f}+")
                record.display_price = ' | '.join(prices) if prices else 'Contact for pricing'
            else:
                if record.asking_rent:
                    record.display_price = f"${record.asking_rent:,.0f}/month"
                else:
                    record.display_price = 'Contact for pricing'

    # === Actions ===
    def action_submit_for_review(self):
        self.write({'approval_status': 'pending'})

    def action_approve(self):
        self.write({'approval_status': 'approved'})

    def action_publish(self):
        self.write({'approval_status': 'published'})

    def action_reject(self):
        self.write({'approval_status': 'rejected'})

    def action_reset_to_draft(self):
        self.write({'approval_status': 'draft'})

    def action_view_images(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Property Images',
            'res_model': 'c21.property.image',
            'view_mode': 'list,form',
            'domain': [('property_id', '=', self.id)],
            'context': {'default_property_id': self.id},
        }

    def action_view_contacts(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Property Contacts',
            'res_model': 'c21.property.contact',
            'view_mode': 'list,form',
            'domain': [('property_id', '=', self.id)],
            'context': {'default_property_id': self.id},
        }
