from odoo import models, fields


class C21PropertyType(models.Model):
    _name = 'c21.property.type'
    _description = 'Property Type'
    _order = 'sequence, name'

    name = fields.Char('Name (EN) / 英文名稱', required=True)
    name_cn = fields.Char('Name (CN) / 中文名稱')
    code = fields.Char('Code / 代碼', required=True)
    sequence = fields.Integer('Sequence', default=10)
    active = fields.Boolean('Active', default=True)

    _code_unique = models.Constraint(
        'UNIQUE(code)',
        'Property type code must be unique!',
    )

    def name_get(self):
        result = []
        for record in self:
            if record.name_cn:
                name = f"{record.name} / {record.name_cn}"
            else:
                name = record.name
            result.append((record.id, name))
        return result
