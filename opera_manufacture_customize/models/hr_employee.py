""" Initialize Hr Employee """

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError, Warning


class HrEmployee(models.Model):
    """
        Inherit Hr Employee:
         -
    """
    _inherit = 'hr.employee'

    is_technical = fields.Boolean()
    cost_per_hour = fields.Float()
    employee_code = fields.Char()

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        super(HrEmployee, self).name_search(name)
        args = args or []
        domain = []
        if name:
            domain = ['|',
                      ('name', operator, name),
                      ('employee_code', operator, name),
                      ]
        results = self.search(domain + args, limit=limit)
        return results.name_get()
