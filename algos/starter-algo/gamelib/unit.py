def is_stationary(unit_type, firewall_types):
    return unit_type in firewall_types

class GameUnit:
    """Holds information about a Unit. 

    Attributes:
        * unit_type (string): This unit's type
        * config (JSON): Contains information about the game
        * player_index (integer): The player that controls this unit. 0 for you, 1 for your opponent.
        * stability (integer): The health of the unit
        * x (integer): The x coordinate of the unit
        * y (integer): The y coordinate of the unit
        * stationary (bool): Whether or not this unit is a firewall
        * speed (float): A unit will move once every 1/speed frames
        * damage (int): The amount of damage this firwall unit will deal to enemy information.
        * damage_f (int): The amount of damage this information unit will deal to enemy firewalls.
        * damage_i (int): The amount of damage this information unit will deal to enemy information.
        * range (float): The effective range of this unit
        * stability (float): The current health of this unit
        * cost (int): The resource cost of this unit

    """
    def __init__(self, unit_type, config, player_index=None, stability=None, x=-1, y=-1):
        """ Initialize unit variables using args passed

        """
        self.unit_type = unit_type
        self.config = config
        self.player_index = player_index
        self.pending_removal = False
        self.x = x
        self.y = y
        self.__serialize_type()
        self.stability = self.max_stability if not stability else stability

    def __serialize_type(self):
        from .game_state import FIREWALL_TYPES, UNIT_TYPE_TO_INDEX, ENCRYPTOR
        self.stationary = is_stationary(self.unit_type, FIREWALL_TYPES)
        type_config = self.config["unitInformation"][UNIT_TYPE_TO_INDEX[self.unit_type]]
        if self.stationary:
            self.speed = 0
            if self.unit_type == ENCRYPTOR:
                self.damage = type_config["shieldAmount"]
            else:
                self.damage = type_config["damage"]
        else:
            self.speed = type_config["speed"]
            self.damage_f = type_config["damageF"]
            self.damage_i = type_config["damageI"]
        self.range = type_config["range"]
        self.max_stability = type_config["stability"]
        self.cost = type_config["cost"]

    def __toString(self):
        owner = "Friendly" if self.player_index == 0 else "Enemy"
        removal = ", pending removal" if self.pending_removal else ""
        return "{} {}, stability: {} location: {}{} ".format(owner, self.unit_type, self.stability, [self.x, self.y], removal)

    def __str__(self):
        return self.__toString()

    def __repr__(self):
        return self.__toString()

