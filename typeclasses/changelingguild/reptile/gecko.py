import math
from random import randint, uniform

from typeclasses.changelingguild.changeling_attack import ChangelingAttack


class Gecko(ChangelingAttack):
    """
    The tails of most geckos serve as nutrient stores, and
    are extremely fragile.  Often acting as decoys in a fight,
    the tails are regenerated by the gecko after several days.
    Tokay geckos are often sold in pet shops.
    """

    energy_cost = 3
    speed = 3
    power = 5
    toughness = 5
    dodge = 5

    def _calculate_damage(self, wielder):
        """
        Calculate the damage of the attack
        """
        dex = wielder.traits.dex.value
        wis = wielder.traits.wis.value
        stat_bonus = (dex + wis) / 5
        base_dmg = 20 + wielder.db.guild_level / 2
        dmg = base_dmg + stat_bonus

        damage = int(uniform(dmg / 2, dmg))
        return damage

    def at_attack(self, wielder, target, **kwargs):
        """
        The auto attack Teiid
        """
        super().at_attack(wielder, target, **kwargs)

        wielder.traits.ep.value -= self.energy_cost
        target.at_damage(wielder, self._calculate_damage(wielder), "edged", "bite")
        target.at_damage(wielder, self._calculate_damage(wielder), "edged", "tail")

        wielder.msg(f"[ Cooldown: {self.speed} seconds ]")
        wielder.cooldowns.add("attack", self.speed)
