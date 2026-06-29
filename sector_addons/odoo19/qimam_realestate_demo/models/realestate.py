from odoo import api, fields, models


class QimamRealEstateProject(models.Model):
    _name = "qimam.realestate.project"
    _description = "Real Estate Project"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "sequence, name"

    name = fields.Char(required=True, tracking=True)
    sequence = fields.Integer(default=10)
    code = fields.Char(tracking=True)
    location = fields.Char(tracking=True)
    developer = fields.Char()
    state = fields.Selection(
        [
            ("planning", "Planning"),
            ("selling", "Selling"),
            ("delivered", "Delivered"),
        ],
        default="selling",
        tracking=True,
    )
    unit_ids = fields.One2many("qimam.realestate.unit", "project_id", string="Units")
    unit_count = fields.Integer(compute="_compute_unit_stats")
    available_unit_count = fields.Integer(compute="_compute_unit_stats")
    reserved_unit_count = fields.Integer(compute="_compute_unit_stats")
    sold_unit_count = fields.Integer(compute="_compute_unit_stats")
    expected_revenue = fields.Float(compute="_compute_unit_stats")

    @api.depends("unit_ids.state", "unit_ids.list_price")
    def _compute_unit_stats(self):
        for project in self:
            units = project.unit_ids
            project.unit_count = len(units)
            project.available_unit_count = len(units.filtered(lambda unit: unit.state == "available"))
            project.reserved_unit_count = len(units.filtered(lambda unit: unit.state == "reserved"))
            project.sold_unit_count = len(units.filtered(lambda unit: unit.state == "sold"))
            project.expected_revenue = sum(units.mapped("list_price"))


class QimamRealEstateUnit(models.Model):
    _name = "qimam.realestate.unit"
    _description = "Real Estate Unit"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "project_id, code"

    name = fields.Char(required=True)
    code = fields.Char(required=True, tracking=True)
    project_id = fields.Many2one("qimam.realestate.project", required=True, ondelete="cascade", tracking=True)
    floor = fields.Char()
    area = fields.Float(string="Area sqm")
    bedroom_count = fields.Integer(string="Bedrooms")
    list_price = fields.Float(string="List Price", tracking=True)
    state = fields.Selection(
        [
            ("available", "Available"),
            ("reserved", "Reserved"),
            ("sold", "Sold"),
        ],
        default="available",
        tracking=True,
    )
    customer_id = fields.Many2one("res.partner", string="Customer", tracking=True)
    reservation_ids = fields.One2many("qimam.realestate.reservation", "unit_id", string="Reservations")

    def action_available(self):
        self.write({"state": "available", "customer_id": False})

    def action_reserved(self):
        self.write({"state": "reserved"})

    def action_sold(self):
        self.write({"state": "sold"})


class QimamRealEstateReservation(models.Model):
    _name = "qimam.realestate.reservation"
    _description = "Real Estate Reservation"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "reservation_date desc, id desc"

    name = fields.Char(required=True, default="New Reservation", tracking=True)
    reservation_date = fields.Date(default=fields.Date.context_today, required=True, tracking=True)
    project_id = fields.Many2one(related="unit_id.project_id", store=True, readonly=True)
    unit_id = fields.Many2one(
        "qimam.realestate.unit",
        required=True,
        domain=[("state", "in", ["available", "reserved"])],
        tracking=True,
    )
    customer_id = fields.Many2one("res.partner", required=True, tracking=True)
    salesperson_id = fields.Many2one("res.users", default=lambda self: self.env.user, tracking=True)
    reservation_amount = fields.Float(tracking=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("reserved", "Reserved"),
            ("confirmed", "Confirmed"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        tracking=True,
    )
    payment_plan_ids = fields.One2many("qimam.realestate.payment.plan", "reservation_id", string="Payment Plan")

    @api.onchange("unit_id")
    def _onchange_unit_id(self):
        if self.unit_id and not self.reservation_amount:
            self.reservation_amount = self.unit_id.list_price * 0.05

    def action_reserve(self):
        for reservation in self:
            reservation.state = "reserved"
            reservation.unit_id.write({
                "state": "reserved",
                "customer_id": reservation.customer_id.id,
            })

    def action_confirm(self):
        for reservation in self:
            reservation.state = "confirmed"
            reservation.unit_id.write({
                "state": "sold",
                "customer_id": reservation.customer_id.id,
            })

    def action_cancel(self):
        for reservation in self:
            reservation.state = "cancelled"
            if reservation.unit_id.customer_id == reservation.customer_id:
                reservation.unit_id.action_available()


class QimamRealEstatePaymentPlan(models.Model):
    _name = "qimam.realestate.payment.plan"
    _description = "Real Estate Payment Plan"
    _order = "sequence, id"

    sequence = fields.Integer(default=10)
    name = fields.Char(required=True)
    reservation_id = fields.Many2one("qimam.realestate.reservation", required=True, ondelete="cascade")
    due_date = fields.Date(required=True)
    amount = fields.Float(required=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("due", "Due"),
            ("paid", "Paid"),
        ],
        default="draft",
    )
