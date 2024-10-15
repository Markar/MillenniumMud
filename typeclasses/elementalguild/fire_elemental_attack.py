from random import uniform
from typeclasses.elementalguild.elemental_attack import ElementalAttack


class FireAttack(ElementalAttack):
    """
    Fire elementals are known for their damage and destruction. They are often
    found in hot areas such as deserts and volcanoes, where they can
    move quickly and easily. Fire elementals have the ability to control
    the fire around them, using it to attack their enemies. They are also
    known for their ability to create powerful flames and explosions, which
    can cause massive damage to their foes.
    """

    speed = 3
    energy_cost = 3

    def _calculate_melee_damage(self, wielder):
        glvl = wielder.db.guild_level
        wis = wielder.traits.wis.value
        intel = wielder.traits.int.value

        stat_bonus = intel / 2 + wis / 2
        dmg = stat_bonus

        if glvl < 10:
            dmg += 7
        elif glvl < 20:
            dmg += 14
        elif glvl < 30:
            dmg += 28
        elif glvl < 40:
            dmg += 42
        else:
            dmg += 65

        dmg += glvl * 3

        damage = int(uniform(dmg / 2, dmg))
        return damage

    def at_attack(self, wielder, target, **kwargs):
        super().at_attack(wielder, target, **kwargs)

        if wielder.db.strategy == "melee":
            self.speed = 3
            self._calculate_melee_damage(wielder)

        # Subtract energy and apply damage to target before their defenses
        wielder.traits.ep.value -= self.energy_cost
        dmg = self._calculate_melee_damage(wielder)
        target.at_damage(wielder, dmg, "fire", "fire_elemental_melee")

        wielder.msg(f"[ Cooldown: {self.speed} seconds ]")
        wielder.cooldowns.add("attack", self.speed)
