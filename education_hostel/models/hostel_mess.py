# -*- coding: utf-8 -*-
from odoo import fields, models


class EducationMess(models.Model):
    _name = 'education.mess'
    _rec_name = "mess_code"
    _description = "Mess"

    mess_name = fields.Char(string="Name", required="True")
    mess_code = fields.Char(string="Code", required="True")
    food_menu = fields.One2many('mess.food', 'mess_rel', string="Food Menu")
    hostel = fields.Many2one('education.hostel', string="Hostel", required="True")

    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda s: s.env['res.company']._company_default_get('ir.sequence'))


class FoodItem(models.Model):
    _name = 'food.item'
    _rec_name = 'name'
    _description = 'Food'

    name = fields.Char(String="Food", required=True)


class MessFoodMenu(models.Model):
    _name = 'mess.food'
    _description = 'Food Order'

    mess_rel = fields.Many2one('education.mess', string="MESS")
    break_fast = fields.Many2one('food.item', string="Break Fast")
    lunch = fields.Many2one('food.item', string="Lunch")
    snack = fields.Many2one('food.item', string="Snack")
    supper = fields.Many2one('food.item', string="Supper")
    week_list = fields.Selection([
        ('MO', 'Monday'),
        ('TU', 'Tuesday'),
        ('WE', 'Wednesday'),
        ('TH', 'Thursday'),
        ('FR', 'Friday'),
        ('SA', 'Saturday'),
        ('SU', 'Sunday')
    ], string='Weekday')


