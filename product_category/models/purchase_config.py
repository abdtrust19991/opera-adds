# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class year_code(models.Model):
    _name = 'year.code'
    _rec_name = 'year'

    year = fields.Char("Year", required=True)
    code = fields.Char("code", required=True)


class menufacture_code(models.Model):
    _name = 'manufacture.code'
    _rec_name = 'manufacture'

    manufacture = fields.Char("Manufacture Name", required=True)
    code = fields.Char("code", required=True)


class season_code(models.Model):
    _name = 'season.code'
    _rec_name = 'season'

    season = fields.Char("Season Name", required=True)
    code = fields.Char("code", required=True)


class activity_code(models.Model):
    _name = 'activity.code'
    _rec_name = 'activity'

    activity = fields.Char("Activity Name", required=True)
    code = fields.Char("code", required=True)


class color_code(models.Model):
    _name = 'color.code'
    _rec_name = 'color'

    color = fields.Char("Color Name", required=True)
    code = fields.Char("code", required=True)


class size_code(models.Model):
    _name = 'size.code'
    _rec_name = 'size'

    size = fields.Char("Size Name", required=True)
    code = fields.Char("code", required=True)
