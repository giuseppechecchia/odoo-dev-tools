import logging

from odoo import models, fields  # , api


_logger = logging.getLogger(__name__)


class CharMapGroups(models.Model):

    _name = 'dev.char.map.groups'
    _description = 'Entity type definition for char mapping model'

    # custom hardcoded grouping
    entities = [
        ('my_custom_group', 'My Custom Group'),
        # Etc
    ]

    name = fields.Selection(
        string='Group name',
        selection=entities
    )

    map_ids = fields.One2many(
        string='Maps',
        comodel_name='dev.char.map',
        inverse_name='entity_id',
    )

    def string_map(self, string):
        self.ensure_one()

        for char in string:
            for map_ in self.map_ids:
                if char == map_.char_from:
                    # ORM return False for null values

                    char_from = map_.char_from
                    char_to = map_.char_to
                    if map_.char_from == '<space>':
                        char_from = ' '
                    if map_.char_to == '<null>':
                        char_to = ''

                    string = string.replace(char_from, char_to)

        return string

    def map_char(self, group, string):
        """
        Returns the purged string based on the entity mapping
        @params:
            group      - Required  : "name" of "dev.char.map.groups"
            string     - Required  : string to purge
        @return:
            res.lang(n)  :   dev.char.map.groups().string_map result
        """

        return self.env['dev.char.map.groups'].search([
            ('name',
             '=',
             group)
        ]).string_map(string)


class DevCharMap(models.Model):

    _name = 'dev.char.map'
    _description = 'Char mapping model'

    _rec_name = 'entity_id'
    # _order = 'char_from'

    char_from = fields.Char(
        string='Original char',
        required=True
    )

    char_to = fields.Char(
        string='New char',
        required=True
    )
    entity_id = fields.Many2one(
        string='Group',
        comodel_name='dev.char.map.groups',
    )

    def write(self, vals):

        char_from = vals.get('char_from')
        char_to = vals.get('char_to')

        if char_from == char_to:
            raise ValueError('The new char must be different '
                             'from the original one')

        return super().write(vals)
