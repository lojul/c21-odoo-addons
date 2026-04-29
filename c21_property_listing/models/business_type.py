from odoo import models, fields


class C21BusinessType(models.Model):
    _name = 'c21.business.type'
    _description = 'Business Type / 業務類型'
    _order = 'sequence, name'

    name = fields.Char('Name (EN) / 英文名稱', required=True)
    name_cn = fields.Char('Name (CN) / 中文名稱', required=True)
    code = fields.Char('Code / 代碼', required=True, index=True)
    sequence = fields.Integer('Sequence', default=10)
    active = fields.Boolean('Active', default=True)

    _code_unique = models.Constraint(
        'UNIQUE(code)',
        'Code must be unique!',
    )
