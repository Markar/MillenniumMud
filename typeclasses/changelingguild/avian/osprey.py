from random import randint, uniform
from typeclasses.changelingguild.changeling_attack import ChangelingAttack


class Osprey(ChangelingAttack):
    """
    Osprey is a bird of prey that is known for its keen eyesight and powerful talons.
    It is often found near bodies of water, where it hunts fish and other aquatic prey.
    Ospreys are solitary animals that are highly territorial and will defend their hunting
    grounds from other predators. They have sharp beaks and claws, which they use to catch
    and kill their prey. Ospreys are also known for their distinctive hovering flight,
    which allows them to spot fish from a distance and dive down to catch them.
    """

    speed = 3
    energy_cost = 3
    power = 12
    toughness = 4
    dodge = 13

    def _calculate_bite_damage(self, wielder):
        dex = wielder.traits.dex.value
        str = wielder.traits.str.value
        stat_bonus = (str + dex) / 5
        dmg = 30 + stat_bonus + wielder.db.guild_level

        damage = int(uniform(dmg / 2, dmg))
        return damage

    def _calculate_claw_damage(self, wielder):
        dex = wielder.traits.dex.value
        str = wielder.traits.str.value
        stat_bonus = (str + dex) / 5
        dmg = stat_bonus + wielder.db.guild_level / 2

        damage = int(uniform(dmg / 2, dmg))
        return damage

    def at_attack(self, wielder, target, **kwargs):
        super().at_attack(wielder, target, **kwargs)

        wielder.traits.ep.value -= self.energy_cost
        target.at_damage(wielder, self._calculate_bite_damage(wielder), "edged", "peck")
        target.at_damage(wielder, self._calculate_claw_damage(wielder), "edged", "claw")
        target.at_damage(wielder, self._calculate_claw_damage(wielder), "edged", "claw")

        wielder.msg(f"[ Cooldown: {self.speed} seconds ]")
        wielder.cooldowns.add("attack", self.speed)
