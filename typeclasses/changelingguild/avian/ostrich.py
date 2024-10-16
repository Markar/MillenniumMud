from random import randint, uniform
from typeclasses.changelingguild.changeling_attack import ChangelingAttack


class Ostrich(ChangelingAttack):
    """
    Ostrich are large, flightless birds known for their speed and agility. They are
    often found in open habitats such as grasslands and deserts, where they hunt
    small mammals and insects. Ostrich have sharp talons and beaks, which they
    use to catch and kill their prey. They are also known for their distinctive
    running speed, which allows them to catch prey in mid-flight. Ostrich are
    solitary birds and are highly territorial, defending their hunting
    grounds from other birds of prey.
    """

    speed = 3
    energy_cost = 3
    power = 10
    toughness = 19
    dodge = 10

    def _calculate_beak_damage(self, wielder):
        str = wielder.traits.str.value
        stat_bonus = str / 3
        dmg = 14 + stat_bonus + wielder.db.guild_level * 2

        damage = int(uniform(dmg / 2, dmg))
        return damage

    def _calculate_wing_damage(self, wielder):
        str = wielder.traits.str.value
        stat_bonus = str / 3
        dmg = 6 + stat_bonus + wielder.db.guild_level

        damage = int(uniform(dmg / 2, dmg))
        return damage

    def at_attack(self, wielder, target, **kwargs):
        super().at_attack(wielder, target, **kwargs)

        wielder.traits.ep.value -= self.energy_cost
        target.at_damage(wielder, self._calculate_beak_damage(wielder), "edged", "bite")
        target.at_damage(wielder, self._calculate_wing_damage(wielder), "blunt", "wing")
        target.at_damage(wielder, self._calculate_wing_damage(wielder), "blunt", "wing")

        wielder.msg(f"[ Cooldown: {self.speed} seconds ]")
        wielder.cooldowns.add("attack", self.speed)
