import math
from random import randint, uniform

from typeclasses.changelingguild.changeling_attack import ChangelingAttack


class Wolverine(ChangelingAttack):
    """
    The wolverine is a stocky and muscular carnivorous mammal that resembles a small bear.
    It is known for its strength, aggression, and tenacity. Wolverines are solitary animals
    that inhabit remote forests and tundra regions. They have sharp claws and powerful jaws,
    which they use to hunt and scavenge for food. Wolverines are also excellent climbers and
    swimmers, allowing them to navigate various terrains. Despite their small size, they are
    feared by many animals due to their ferocity and ability to take down prey much larger than
    themselves.
    """

    damage = 1
    energy_cost = 3
    skill = "edged"
    name = "claw"
    speed = 3
    power = 22
    toughness = 10
    dodge = 6

    def _calculate_bite_damage(self, wielder):
        dex = wielder.traits.dex.value
        str = wielder.traits.str.value
        stat_bonus = str / 10 + dex / 5
        dmg = 7 + stat_bonus + wielder.db.guild_level / 2

        damage = int(uniform(dmg / 2, dmg))
        return damage

    def _calculate_claw_damage(self, wielder):
        dex = wielder.traits.dex.value
        str = wielder.traits.str.value
        stat_bonus = str / 10 + dex / 5
        dmg = 2 + stat_bonus + wielder.db.guild_level / 4

        damage = int(uniform(dmg / 2, dmg))
        return damage

    def at_attack(self, wielder, target, **kwargs):
        super().at_attack(wielder, target, **kwargs)

        wielder.traits.ep.value -= self.energy_cost
        target.at_damage(wielder, self._calculate_bite_damage(wielder), "edged", "bite")
        target.at_damage(wielder, self._calculate_claw_damage(wielder), "edged", "claw")
        target.at_damage(wielder, self._calculate_claw_damage(wielder), "edged", "claw")
        target.at_damage(wielder, self._calculate_claw_damage(wielder), "edged", "claw")
        target.at_damage(wielder, self._calculate_claw_damage(wielder), "edged", "claw")

        wielder.msg(f"[ Cooldown: {self.speed} seconds ]")
        wielder.cooldowns.add("attack", self.speed)
