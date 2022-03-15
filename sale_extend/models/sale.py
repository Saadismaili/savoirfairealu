# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.addons import decimal_precision as dp


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            qty = line.product_uom_qty

            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, qty,
                                            product=line.product_id, partner=line.order_id.partner_shipping_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })

    height = fields.Float(string='Hauteur', digits=dp.get_precision('Vitrage unite'), required=True,
                          default=1.0)
    width = fields.Float(string='Largueur', digits=dp.get_precision('Vitrage unite'), required=True,
                          default=1.0)
    compute_type = fields.Selection([('calculee', u'Calculé'),
                                     ('simple', u'Simple')], String='Type de Calcul', store=True,
                                    related='product_id.compute_type')
    type = fields.Selection([('aluminium', 'Aluminium'),
                             ('travaux', 'Travaux'),
                             ('volet_roulant', 'Volet roulant'),
                             ('vitrage', 'Vitrage'),
                             ('rideau', 'Rideau'),
                             ], string="Type devis")
    product_type_id = fields.Many2one('product.type', string='Vitrage')
    code = fields.Char('Code')
    niveau = fields.Many2one('sale.line.niveau', string='Niveau')
    emplacement = fields.Many2one('sale.line.emplacement', string='Emplacement')
    type_moteur = fields.Many2one('sale.type.moteur', string='Type de moteur')
    prix_metre_caree = fields.Float(u'Prix au mètre carrée')

    @api.onchange('prix_metre_caree', 'width', 'height')
    def _update_unit_price(self):
        price_unit = self.height * self.width * self.prix_metre_caree
        self.price_unit = price_unit

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        if not self.product_uom or not self.product_id:
            self.price_unit = 0.0
            return
        if self.order_id.pricelist_id and self.order_id.partner_id:
            product = self.product_id.with_context(
                lang=self.order_id.partner_id.lang,
                partner=self.order_id.partner_id.id,
                quantity=self.product_uom_qty,
                date=self.order_id.date_order,
                pricelist=self.order_id.pricelist_id.id,
                uom=self.product_uom.id,
                fiscal_position=self.env.context.get('fiscal_position')
            )
            self.price_unit = self.env['account.tax']._fix_tax_included_price_company(
                self.price_unit, product.taxes_id, self.tax_id, self.company_id)

    # @api.multi
    def _prepare_invoice_line(self, qty):
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        res.update({
            'width': self.width,
            'height': self.height,
            'type': self.type,
            'product_type_id': self.product_type_id.id,
            'code': self.code,
            'niveau': self.niveau.id,
            'emplacement': self.emplacement.id,
            'type_moteur': self.type_moteur.id,

        })
        return res

    # @api.multi
    @api.onchange('product_type_id')
    def product_type_id_change(self):
        if self.product_type_id:
            self.name = self.name + ' ' +str(self.product_type_id.name)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    description = fields.Text(string='Description')

    # @api.multi
    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        res.update({
            'description': self.description
        })
        return res

    # @api.multi
    def get_type_devis(self):
        distinct_lst, result = [], False
        for rec in self:
            type = rec.order_line.mapped('type')
        distinct_lst = list(set(type))
        if len(distinct_lst) == 1 and 'travaux' in distinct_lst:
            result = 'travaux'
        elif len(distinct_lst) == 1 and 'rideau' in distinct_lst:
            result = 'rideau'
        return result

    # @api.multi
    def _get_tax_amount_by_group(self):
        self.ensure_one()
        res = {}
        for line in self.order_line:
            price_reduce = line.price_unit * (1.0 - line.discount / 100.0)
            qty = line.product_uom_qty
            taxes = line.tax_id.compute_all(price_reduce, quantity=qty, product=line.product_id, partner=self.partner_shipping_id)['taxes']
            for tax in line.tax_id:
                group = tax.tax_group_id
                res.setdefault(group, {'amount': 0.0, 'base': 0.0})
                for t in taxes:
                    if t['id'] == tax.id or t['id'] in tax.children_tax_ids.ids:
                        res[group]['amount'] += t['amount']
                        res[group]['base'] += t['base']
        res = sorted(res.items(), key=lambda l: l[0].sequence)
        res = [(l[0].name, l[1]['amount'], l[1]['base'], len(res)) for l in res]
        return res


class SaleLineNiveau(models.Model):
    _name = 'sale.line.niveau'

    name = fields.Char(string='Nom', required=True)


class SaleLineEmplacement(models.Model):
    _name = 'sale.line.emplacement'

    name = fields.Char(string='Nom', required=True)


class SaleLineTypeMoteur(models.Model):
    _name = 'sale.type.moteur'

    name = fields.Char(string='Nom', required=True)

