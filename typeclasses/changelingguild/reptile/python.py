from random import randint, uniform
from typeclasses.changelingguild.changeling_attack import ChangelingAttack


class Python(ChangelingAttack):
    """
    Most species are secretive ground dwellers or burrowers,
    and may show such adaptations as a clear ("window") scale
    on the lower eyelid, reduction or loss of limbs, and
    sunken eardrumms.  Some are arboreal or somewhat aquatic.
    """

    speed = 3
    energy_cost = 3
    power = 12
    toughness = 8
    dodge = 7

    def _calculate_bite_damage(self, wielder):
        str = wielder.traits.str.value
        stat_bonus = str / 2
        base_dmg = 10 + wielder.db.guild_level / 2
        dmg = base_dmg + stat_bonus

        damage = int(uniform(dmg / 2, dmg))
        return damage

    def _calculate_constrict_damage(self, wielder):
        str = wielder.traits.str.value

        stat_bonus = str / 2
        base_dmg = 20 + wielder.db.guild_level * 2
        dmg = base_dmg + stat_bonus

        damage = int(uniform(dmg / 2, dmg))
        return damage

    def at_attack(self, wielder, target, **kwargs):
        super().at_attack(wielder, target, **kwargs)

        wielder.traits.ep.value -= self.energy_cost
        target.at_damage(wielder, self._calculate_bite_damage(wielder), "edged", "bite")
        target.at_damage(
            wielder, self._calculate_constrict_damage(wielder), "blunt", "constrict"
        )

        wielder.msg(f"[ Cooldown: {self.speed} seconds ]")
        wielder.cooldowns.add("attack", self.speed)
