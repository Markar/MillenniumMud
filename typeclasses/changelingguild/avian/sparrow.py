from random import randint, uniform
from typeclasses.changelingguild.changeling_attack import ChangelingAttack


class Sparrow(ChangelingAttack):
    """
    Sparrows are small, fast birds that are known for their
    agility and quick reflexes. They are often found in
    urban environments and are known for their distinctive
    chirping songs.
    """

    speed = 3
    energy_cost = 3

    power = 3
    toughness = 2
    dodge = 3

    def _calculate_bite_damage(self, wielder):
        dex = wielder.traits.dex.value
        str = wielder.traits.str.value
        stat_bonus = str + dex / 5
        dmg = 10 + stat_bonus + wielder.db.guild_level / 2

        damage = int(uniform(dmg / 2, dmg))
        return damage

    def at_attack(self, wielder, target, **kwargs):
        super().at_attack(wielder, target, **kwargs)

        wielder.traits.ep.value -= self.energy_cost
        target.at_damage(wielder, self._calculate_bite_damage(wielder), "edged", "bite")
        target.at_damage(wielder, self._calculate_bite_damage(wielder), "edged", "bite")

        wielder.msg(f"[ Cooldown: {self.speed} seconds ]")
        wielder.cooldowns.add("attack", self.speed)
