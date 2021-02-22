def is_stationary(unit_type, structure_types):
    """
        Args:
            unit_type: A unit type
        
        Returns: 
            Boolean, True if the unit is stationary, False otherwise.
    """
    return unit_type in structure_types


class GameUnit:
    """Holds information about a Unit. 

    Attributes :
        * unit_type (string): This unit's type
        * config (JSON): Contains information about the game
        * player_index (integer): The player that controls this unit. 0 for you, 1 for your opponent.
        * x (integer): The x coordinate of the unit
        * y (integer): The y coordinate of the unit
        * stationary (bool): Whether or not this unit is a structures
        * speed (float): A unit will move once every 1/speed frames
        * damage_f (int): The amount of damage this mobile unit will deal to enemy structures.
        * damage_i (int): The amount of damage this mobile unit will deal to enemy mobile units.
        * attackRange (float): The effective range of this unit for attacking
        * shieldRange (float): The effective range of this unit for shielding
        * max_health (float): The starting health of this unit. Note than 'health' can be increased beyond this value by shielding in some game configurations.
        * health (float): The current health of this unit
        * cost ([int, int]): The resource costs of this unit first is SP second is MP
        * shieldPerUnit (float): how much shield is given per unit
        * pending_removal (boolean): If this unit is marked for removal by its owner
        * upgraded (boolean): If this unit is upgraded

    """
    def __init__(self, unit_type, config, player_index=None, health=None, x=-1, y=-1):
        """ Initialize unit variables using args passed

        """
        self.unit_type = unit_type
        self.config = config
        self.player_index = player_index
        self.pending_removal = False
        self.upgraded = False
        self.x = x
        self.y = y
        self.__serialize_type()
        self.health = self.max_health if not health else health

    def __serialize_type(self):
        from .game_state import STRUCTURE_TYPES, UNIT_TYPE_TO_INDEX, SUPPORT
        type_config = self.config["unitInformation"][UNIT_TYPE_TO_INDEX[self.unit_type]]
        self.stationary = type_config["unitCategory"] == 0
        self.speed = type_config.get("speed", 0)
        self.damage_f = type_config.get("attackDamageTower", 0)
        self.damage_i = type_config.get("attackDamageWalker", 0)
        self.attackRange = type_config.get("attackRange", 0)
        self.shieldRange = type_config.get("shieldRange", 0)
        self.max_health = type_config.get("startHealth", 0)
        self.shieldPerUnit = type_config.get("shieldPerUnit", 0)
        self.cost = [type_config.get("cost1", 0), type_config.get("cost2", 0)]


    def upgrade(self):
        from .game_state import UNIT_TYPE_TO_INDEX
        type_config = self.config["unitInformation"][UNIT_TYPE_TO_INDEX[self.unit_type]].get("upgrade", {})
        self.speed = type_config.get("speed", self.speed)
        self.damage_f = type_config.get("attackDamageTower", self.damage_f)
        self.damage_i = type_config.get("attackDamageWalker", self.damage_i)
        self.attackRange = type_config.get("attackRange", self.attackRange)
        self.shieldRange = type_config.get("shieldRange", self.shieldRange)
        self.max_health = type_config.get("startHealth", self.max_health)
        self.shieldPerUnit = type_config.get("shieldPerUnit", self.shieldPerUnit)
        self.cost = [type_config.get("cost1", 0) + self.cost[0], type_config.get("cost2", 0) + self.cost[1]]
        self.upgraded = True


    def __toString(self):
        owner = "Friendly" if self.player_index == 0 else "Enemy"
        removal = ", pending removal" if self.pending_removal else ""
        return "{} {}, health: {} location: {} removal: {} upgrade: {} ".format(owner, self.unit_type, self.health, [self.x, self.y], removal, self.upgraded)

    def __str__(self):
        return self.__toString()

    def __repr__(self):
        return self.__toString()

