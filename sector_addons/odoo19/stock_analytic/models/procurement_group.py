from odoo import fields, models


class ProcurementGroup(models.Model):
    _name = "procurement.group"
    _description = "Procurement Group Compatibility"

    name = fields.Char(required=True)
    move_type = fields.Selection(
        [("direct", "As soon as possible"), ("one", "When all products are ready")],
        default="direct",
        required=True,
    )
    partner_id = fields.Many2one("res.partner")
    stock_move_ids = fields.One2many("stock.move", "group_id")


class StockPicking(models.Model):
    _inherit = "stock.picking"

    group_id = fields.Many2one("procurement.group", copy=False)


class StockMove(models.Model):
    _inherit = "stock.move"

    group_id = fields.Many2one("procurement.group", copy=False)
