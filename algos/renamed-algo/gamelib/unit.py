def is_stationary(unit_type, firewall_types):
    return unit_type in firewall_types

class GameUnit:
    '''
    Class that holds information about a unit. Uses the config file. Useful for tracking what units are, where on the map
    their current stability, and also can be used with default parameters to check how much a unit type costs, its range etc.
    '''
    def __init__(self, unit_type, config, player_id=None, stability=None, unit_id="", x=-1, y=-1):
        self.unit_type = unit_type
        self.config = config
        self.player_id = player_id
        self.unit_id = unit_id
        self.pending_removal = False
        self.x = x
        self.y = y
        self.__serialize_type()
        self.stability = self.max_stability if not stability else stability

    def __serialize_type(self):
        from .game import FIREWALL_TYPES, UNIT_TYPE_TO_INDEX, ENCRYPTOR
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
            self.damage_t = type_config["damageF"]
            self.damage_s = type_config["damageI"]
        self.range = type_config["range"]
        self.max_stability = type_config["stability"]
        self.hitbox = type_config["getHitRadius"]
        self.cost = type_config["cost"]

    def __toString(self):
        owner = "Friendly" if self.player_id == 0 else "Enemy"
        removal = ", pending removal" if self.pending_removal else ""
        return "{} {}, stability: {} location: {} {} ".format(owner, self.unit_type, self.stability, [self.x, self.y], removal)

    def __str__(self):
        return self.__toString()

    def __repr__(self):
        return self.__toString()

