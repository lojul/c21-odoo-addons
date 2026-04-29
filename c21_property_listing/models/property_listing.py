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
    ('sai_ying_pun', 'Sai Ying Pun (西營盤)'),
    # Kowloon
    ('tsim_sha_tsui', 'Tsim Sha Tsui (尖沙咀)'),
    ('jordan', 'Jordan (佐敦)'),
    ('mong_kok', 'Mong Kok (旺角)'),
    ('kowloon_bay', 'Kowloon Bay (九龍灣)'),
    ('kwun_tong', 'Kwun Tong (觀塘)'),
    ('san_po_kong', 'San Po Kong (新蒲崗)'),
    ('cheung_sha_wan', 'Cheung Sha Wan (長沙灣)'),
    ('sham_shui_po', 'Sham Shui Po (深水埗)'),
    ('whampoa', 'Whampoa (黃埔)'),
    # New Territories
    ('kwai_chung', 'Kwai Chung (葵涌)'),
    ('tsuen_wan', 'Tsuen Wan (荃灣)'),
    ('sha_tin', 'Sha Tin (沙田)'),
    ('fo_tan', 'Fo Tan (火炭)'),
    ('tuen_mun', 'Tuen Mun (屯門)'),
    ('yuen_long', 'Yuen Long (元朗)'),
    ('po_lam', 'Po Lam (寶琳)'),
    ('tai_po', 'Tai Po (大埔)'),
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
        'Ref Code / 編號', required=True, index=True,
        help='Unique reference code (e.g., C0000063 for co-working, LS-0001 for leasing)')
    name = fields.Char('English Name / 英文名稱', required=True)
    name_cn = fields.Char('Chinese Name / 中文名稱')
    listing_type = fields.Selection([
        ('coworking', 'Co-working Space'),
        ('leasing', 'Leasing Property'),
    ], string='Type / 類型', required=True, default='leasing')

    # === Location ===
    district = fields.Selection(
        DISTRICT_SELECTION, string='District / 地區', required=True, index=True)
    building_name = fields.Char('Building / 大廈')
    address = fields.Char('Street / 街道')
    floor = fields.Char('Floor / 樓層')
    unit = fields.Char('Unit / 單位')
    latitude = fields.Float('Lat / 緯度', digits=(10, 7))
    longitude = fields.Float('Lng / 經度', digits=(10, 7))

    # === Status & Workflow ===
    state = fields.Selection([
        ('available', 'Available'),
        ('under_negotiation', 'Under Negotiation'),
        ('leased', 'Leased'),
        ('off_market', 'Off Market'),
    ], string='Status / 狀態', default='available', index=True, tracking=True)

    approval_status = fields.Selection([
        ('draft', 'Draft'),
        ('ready', 'Ready to Publish'),
        ('published', 'Published'),
    ], string='Publish / 發佈', default='draft', index=True, tracking=True,
       group_expand='_group_expand_approval_status')

    available_from = fields.Date('Available / 可租日')

    # === Co-working Specific Fields ===
    operator_id = fields.Many2one(
        'res.partner', string='Operator / 營運商',
        domain=[('is_property_operator', '=', True), ('is_company', '=', True)])
    capacity = fields.Integer('Capacity / 容量', help='Total people capacity')
    available_capacity = fields.Integer('Avail Cap / 可用')
    size = fields.Integer('Size sqft / 面積', help='Total size in square feet')
    hot_desk_price = fields.Monetary('Hot Desk / 流動位', help='Monthly price for hot desk in HKD')
    dedicated_desk_price = fields.Monetary('Dedicated / 固定位', help='Monthly price for dedicated desk in HKD')
    office_price = fields.Monetary('Office / 辦公室', help='Monthly starting price for private office in HKD')

    # === Leasing Specific Fields ===
    property_type_id = fields.Many2one(
        'c21.property.type', string='Prop Type / 物業類型',
        ondelete='restrict', index=True)

    building_grade = fields.Selection([
        ('grade_a', 'Grade A'),
        ('grade_b', 'Grade B'),
        ('grade_c', 'Grade C'),
    ], string='Grade / 寫字樓級別')

    business_type_id = fields.Many2one(
        'c21.business.type', string='Business / 業務類型',
        ondelete='restrict', index=True,
        help='For retail properties')

    # Area fields
    gross_area = fields.Float('Gross sqft / 建呎', digits=(12, 2))
    net_area = fields.Float('Net sqft / 實呎', digits=(12, 2))
    total_area = fields.Float(
        'Total Area / 總面積', digits=(12, 2), compute='_compute_total_area', store=True)

    # Rental fields
    asking_rent = fields.Monetary('Rent / 租價', help='Monthly asking rent in HKD')
    floor_rent = fields.Monetary('Floor Rent / 底租', help='Minimum acceptable rent')
    rent_per_sqft = fields.Float(
        'Rent/sqft / 租呎價', digits=(12, 2), compute='_compute_rent_per_sqft', store=True)
    floor_rent_per_sqft = fields.Float(
        'Floor Rent/sqft / 底租呎價', digits=(12, 2), compute='_compute_floor_rent_per_sqft', store=True)

    # Sale fields
    selling_price = fields.Float('Sale Price / 售價(萬)', digits=(12, 2), help='Selling price in 萬 (10k HKD)')
    floor_selling_price = fields.Float('Floor Sale / 底售(萬)', digits=(12, 2), help='Minimum selling price in 萬')
    sale_price_per_sqft = fields.Float(
        'Sale/sqft / 售呎價', digits=(12, 2), compute='_compute_sale_price_per_sqft', store=True)
    floor_sale_per_sqft = fields.Float(
        'Floor Sale/sqft / 底售呎價', digits=(12, 2), compute='_compute_floor_sale_per_sqft', store=True)
    yield_rate = fields.Float(
        'Yield / 回報率', digits=(5, 2), compute='_compute_yield_rate', store=True,
        help='Annual yield rate in %')

    # Property details
    room_layout = fields.Selection([
        ('studio', 'Studio / 開放式'),
        ('1br', '1 Room / 1房'),
        ('2br', '2 Rooms / 2房'),
        ('3br', '3 Rooms / 3房'),
        ('4br_plus', '4+ Rooms / 4房+'),
    ], string='Layout / 間隔')

    lease_terms = fields.Char('Lease / 租約', help='e.g., 2 years minimum')
    year_built = fields.Char('Year Built / 樓齡')
    total_floors = fields.Integer('Floors / 總樓層')
    parking_number = fields.Char('Parking No. / 車位號碼')
    dd_lot = fields.Char('DD Lot / 地段編號', help='Land registry reference')

    # Tenant info
    tenant_name = fields.Char('Tenant / 租客')

    # === Operations & Tracking ===
    source_id = fields.Many2one(
        'c21.property.source', string='Source / 來源',
        ondelete='restrict', index=True)

    key_holder = fields.Char('Key Holder / 鎖匙')
    internal_notes = fields.Text('Notes / 提示', help='Internal notes for staff')
    listing_date = fields.Date('Listing Date / 開盤日期')
    followup_date = fields.Date('Follow-up / 跟進日期')
    user_id = fields.Many2one('res.users', string='Responsible / 負責同事', default=lambda self: self.env.user, tracking=True)

    # === Descriptions ===
    description = fields.Html('Desc (EN) / 描述')
    description_cn = fields.Html('Desc (CN) / 中文描述')

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
    image_count = fields.Integer('Images', compute='_compute_image_count')
    contact_count = fields.Integer('Contacts', compute='_compute_contact_count')
    display_price = fields.Char('Price / 價格', compute='_compute_display_price')

    _ref_code_unique = models.Constraint(
        'UNIQUE(ref_code)',
        'Reference code must be unique!',
    )

    @api.model
    def _group_expand_approval_status(self, states, domain):
        """Show all approval status columns in Kanban even when empty."""
        return [key for key, val in self._fields['approval_status'].selection]

    @api.depends('gross_area', 'net_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = (record.gross_area or 0) + (record.net_area or 0)

    @api.depends('asking_rent', 'net_area')
    def _compute_rent_per_sqft(self):
        for record in self:
            if record.net_area and record.net_area > 0:
                record.rent_per_sqft = record.asking_rent / record.net_area
            else:
                record.rent_per_sqft = 0

    @api.depends('floor_rent', 'net_area')
    def _compute_floor_rent_per_sqft(self):
        for record in self:
            if record.net_area and record.net_area > 0:
                record.floor_rent_per_sqft = (record.floor_rent or 0) / record.net_area
            else:
                record.floor_rent_per_sqft = 0

    @api.depends('selling_price', 'net_area')
    def _compute_sale_price_per_sqft(self):
        for record in self:
            if record.net_area and record.net_area > 0 and record.selling_price:
                # selling_price is in 萬 (10k), convert to HKD for per sqft
                record.sale_price_per_sqft = (record.selling_price * 10000) / record.net_area
            else:
                record.sale_price_per_sqft = 0

    @api.depends('floor_selling_price', 'net_area')
    def _compute_floor_sale_per_sqft(self):
        for record in self:
            if record.net_area and record.net_area > 0 and record.floor_selling_price:
                record.floor_sale_per_sqft = (record.floor_selling_price * 10000) / record.net_area
            else:
                record.floor_sale_per_sqft = 0

    @api.depends('asking_rent', 'selling_price')
    def _compute_yield_rate(self):
        for record in self:
            if record.selling_price and record.selling_price > 0 and record.asking_rent:
                # Annual yield = (monthly rent * 12) / (selling price in HKD) * 100
                annual_rent = record.asking_rent * 12
                selling_price_hkd = record.selling_price * 10000
                record.yield_rate = (annual_rent / selling_price_hkd) * 100
            else:
                record.yield_rate = 0

    @api.depends('image_ids')
    def _compute_image_count(self):
        # Batch compute to avoid N+1 queries
        if not self.ids:
            for record in self:
                record.image_count = 0
            return
        data = self.env['c21.property.image'].read_group(
            [('property_id', 'in', self.ids)],
            ['property_id'],
            ['property_id']
        )
        mapped = {d['property_id'][0]: d['property_id_count'] for d in data}
        for record in self:
            record.image_count = mapped.get(record.id, 0)

    @api.depends('contact_ids')
    def _compute_contact_count(self):
        # Batch compute to avoid N+1 queries
        if not self.ids:
            for record in self:
                record.contact_count = 0
            return
        data = self.env['c21.property.contact'].read_group(
            [('property_id', 'in', self.ids)],
            ['property_id'],
            ['property_id']
        )
        mapped = {d['property_id'][0]: d['property_id_count'] for d in data}
        for record in self:
            record.contact_count = mapped.get(record.id, 0)

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
    def action_set_ready(self):
        self.write({'approval_status': 'ready'})

    def action_publish(self):
        self.write({'approval_status': 'published'})

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

    def action_open_form(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': self.name,
            'res_model': 'c21.property.listing',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'current',
        }
