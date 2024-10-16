from random import randint, uniform
from typeclasses.changelingguild.changeling_attack import ChangelingAttack


class Owl(ChangelingAttack):
    """
    Owl is a bird of prey that is known for its nocturnal habits and silent flight.
    It has keen eyesight and hearing, which allows it to hunt in the dark. Owls are
    solitary animals that are highly territorial and will defend their hunting grounds
    from other predators. They have sharp talons and beaks, which they use to catch
    and kill their prey. Owls are also known for their distinctive hooting calls,
    which they use to communicate with other owls and establish their territory.
    """

    speed = 3
    energy_cost = 3
    power = 23
    toughness = 9
    dodge = 10

    def _calculate_bite_damage(self, wielder):
        dex = wielder.traits.dex.value
        str = wielder.traits.str.value
        stat_bonus = str / 3 + dex / 5
        dmg = 14 + stat_bonus + wielder.db.guild_level / 2

        damage = int(uniform(dmg / 2, dmg))
        return damage

    def _calculate_gaze_damage(self, wielder):
        wis = wielder.traits.wis.value
        stat_bonus = wis / 3
        dmg = 39 + stat_bonus + wielder.db.guild_level

        damage = int(uniform(dmg / 2, dmg))
        return damage

    def at_attack(self, wielder, target, **kwargs):
        super().at_attack(wielder, target, **kwargs)

        wielder.traits.ep.value -= self.energy_cost
        target.at_damage(wielder, self._calculate_bite_damage(wielder), "edged", "peck")
        target.at_damage(wielder, self._calculate_gaze_damage(wielder), "mind", "gaze")

        wielder.msg(f"[ Cooldown: {self.speed} seconds ]")
        wielder.cooldowns.add("attack", self.speed)
