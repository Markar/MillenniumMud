from random import randint, uniform

from typeclasses.changelingguild.changeling_attack import ChangelingAttack


class BlackBear(ChangelingAttack):
    """
    The black bear is a large mammal that is native to North America. It is known for its
    strength and agility, as well as its ability to climb trees and swim. Black bears are
    omnivorous and will eat a variety of foods, including berries, nuts, fish, and small
    mammals. They are solitary animals and are highly territorial, defending their hunting
    grounds from other bears. Black bears are also known for their distinctive hump on their
    shoulders, which is made of muscle and helps them dig and climb.
    """

    energy_cost = 3
    speed = 3
    power = 17
    toughness = 14
    dodge = 14

    def _calculate_bite_damage(self, wielder):
        str = wielder.traits.str.value
        stat_bonus = str / 4
        dmg = 16 + stat_bonus + wielder.db.guild_level

        damage = int(uniform(dmg / 2, dmg))
        return damage

    def _calculate_claw_damage(self, wielder):
        str = wielder.traits.str.value
        stat_bonus = str / 4
        dmg = 5 + stat_bonus + wielder.db.guild_level / 3

        damage = int(uniform(dmg / 2, dmg))
        return damage

    def _calculate_hug_damage(self, wielder):
        str = wielder.traits.str.value
        stat_bonus = str / 4
        dmg = 28 + stat_bonus + wielder.db.guild_level * 2

        damage = int(uniform(dmg / 2, dmg))
        return damage

    def at_attack(self, wielder, target, **kwargs):
        super().at_attack(wielder, target, **kwargs)

        wielder.traits.ep.value -= self.energy_cost
        target.at_damage(wielder, self._calculate_bite_damage(wielder), "edged", "bite")
        target.at_damage(wielder, self._calculate_claw_damage(wielder), "edged", "bite")
        target.at_damage(wielder, self._calculate_claw_damage(wielder), "edged", "bite")
        target.at_damage(wielder, self._calculate_hug_damage(wielder), "blunt", "hug")

        wielder.msg(f"[ Cooldown: {self.speed} seconds ]")
        wielder.cooldowns.add("attack", self.speed)
