from random import uniform, randint
from evennia.utils import delay, iter_to_str
from evennia import TICKER_HANDLER as tickerhandler
from commands.elemental_cmds import ElementalCmdSet
from typeclasses.elementalguild.earth_elemental_attack import EarthAttack
from typeclasses.elementals import Elemental
from typeclasses.elementalguild.attack_emotes import AttackEmotes
from typeclasses.utils import geHealthStatus
import math


class EarthElemental(Elemental):

    def at_object_creation(self):
        self.cmdset.add(ElementalCmdSet, persistent=True)
        super().at_object_creation()
        con_increase_amount = 15
        int_increase_amount = 10
        self.db.con_increase_amount = con_increase_amount
        self.db.int_increase_amount = int_increase_amount
        self.traits.hp.base = 50 + (con_increase_amount * self.traits.con.value)
        self.traits.fp.base = 50 + (int_increase_amount * self.traits.int.value)

        self.db.guild_level = 1
        self.db.gxp = 0
        self.db.skill_gxp = 0
        self.db.title = "the novice earth elemental"

        self.db.natural_weapon = {
            "name": "earth_attack",
            "damage_type": "blunt",
            "damage": 12,
            "speed": 3,
            "energy_cost": 10,
        }
        self.db.guild = "elemental"
        self.db.subguild = "earth"
        self.db._wielded = {"left": None, "right": None}
        self.db.reaction_percentage = 50
        self.db.hpregen = 1
        self.db.fpregen = 1
        self.db.epregen = 1
        self.db.strategy = "melee"
        self.db.skills = {
            "stone mastery": 1,
            "earth resonance": 1,
            "mineral fortification": 1,
            "geological insight": 1,
            "seismic awareness": 1,
            "rock solid defense": 1,
            "elemental harmony": 1,
            "earthen regeneration": 1,
        }
        self.db.active_form = None

        self.db.stone_skin = False
        self.db.earth_shield = {"hits": 0}
        self.db.mountain_stance = False
        self.db.earthen_renewal = {"duration": 0, "rate": 0}
        self.db.burnout = {"active": False, "count": 0, "max": 0, "duration": 0}
        self.db.elemental_fury = {"active": False, "duration": 0}
        self.db.primordial_essence = {"count": 0, "max": 0}

        tickerhandler.add(
            interval=6, callback=self.at_tick, idstring=f"{self}-regen", persistent=True
        )

    def get_display_status(self, looker, **kwargs):
        """
        Returns a quick view of the current status of this character
        """

        chunks = []

        # add resource levels
        hp = int(self.traits.hp.current)
        hpmax = int(self.traits.hp.base)
        fp = int(self.traits.fp.current)
        fpmax = int(self.traits.fp.base)
        ep = int(self.traits.ep.current)
        epmax = int(self.traits.ep.base)
        # burnout_count = self.db.burnout["count"]
        # burnout_max = self.db.burnout["max"]
        primordial_energy = self.db.primordial_essence["count"]
        PE_Max = self.db.primordial_essence["max"]

        chunks.append(
            f"|320Health: |400{hp}/{hpmax}|320 Focus: |015{fp}/{fpmax}|320 Energy: |215{ep}/{epmax}|g"
        )
        if self.db.guild_level > 6:
            chunks.append(f"|510Essence: |510{primordial_energy}/{PE_Max}|n")
        if self.db.burnout["active"]:
            chunks.append(f"|YB")
        if self.db.elemental_fury["active"]:
            chunks.append(f"|YEF")

        if self.db.active_form == "earth":
            chunks.append(f"|320Earth")

        if self.db.stone_skin:
            chunks.append(f"|YSS")
        if self.db.earth_shield and self.db.earth_shield["hits"] > 0:
            chunks.append(f"|YES")
        if self.db.mountain_stance:
            chunks.append(f"|YMS")
        if self.db.earthen_renewal and self.db.earthen_renewal["duration"] > 0:
            chunks.append(f"|YER")

        if looker != self:
            chunks.append(f"|gE: |G{looker.get_display_name(self, **kwargs)}")
            hpPct = looker.traits.hp.current / looker.traits.hp.base
            status = geHealthStatus(self, hpPct)
            chunks.append(f"|gH: |G{status}")
            if self.key == "Markar":
                chunks.append(f"M-{looker.traits.hp.current} / {looker.traits.hp.base}")

        # get all the current status flags for this character
        if status_tags := self.tags.get(category="status", return_list=True):
            # add these statuses to the string, if there are any
            chunks.append(iter_to_str(status_tags))

        if looker == self:
            # if we're checking our own status, include cooldowns
            all_cooldowns = [
                (key, self.cooldowns.time_left(key, use_int=True))
                for key in self.cooldowns.all
            ]
            all_cooldowns = [f"{c[0]} ({c[1]}s)" for c in all_cooldowns if c[1]]
            if all_cooldowns:
                chunks.append(f"Cooldowns: {iter_to_str(all_cooldowns, endsep=',')}")
        chunks.append(f"\n")
        # glue together the chunks and return
        return " - ".join(chunks)

    def at_essence_tick(self):
        """
        Regenerate essence points.
        """
        glvl = self.db.guild_level
        if glvl < 7:
            return
        self.msg(
            f"|cThe earth beneath you rumbles and shifts, infusing you with a surge of energy!|n"
        )
        current = self.db.primordial_essence["count"]
        max = self.db.primordial_essence["max"]
        harmony = self.db.skills["elemental harmony"]

        self.db.primordial_essence["count"] = min(current + harmony + (glvl * 0.5), max)

    def at_tick(self):
        base_regen = self.db.hpregen
        base_ep_regen = self.db.epregen
        base_fp_regen = self.db.fpregen
        regen = self.db.skills["earthen regeneration"]

        if regen < 2:
            bonus_fp = 0
        if regen < 5:
            bonus_fp = int(uniform(0, regen / 2))  # 0-2
        if regen < 10:
            bonus_fp = int(uniform(1, regen / 2))  # 1-3
        if regen < 15:
            bonus_fp = int(uniform(3, regen / 3))  # 3-5
        if regen < 20:
            bonus_fp = int(uniform(4, regen / 3))  # 4-6

        if self.db.earthen_renewal:
            if self.db.earthen_renewal["duration"] > 0:
                rate = self.db.earthen_renewal["rate"]
                bonus_fp += uniform(rate / 2, rate + 1)
                if self.db.earthen_renewal["duration"] == 1:
                    deactivateMsg = f"|C$Your() body stops glowing as you release the regenerative energy."
                    self.location.msg_contents(deactivateMsg, from_obj=self)
                self.db.earthen_renewal["duration"] -= 1

        if self.db.burnout["active"]:
            if self.db.burnout["duration"] == 1:
                self.db.burnout["active"] = False
                deactivateMsg = f"|CThe flames around you flicker and die out, leaving you feeling drained."
                self.location.msg_contents(deactivateMsg, from_obj=self)
            self.db.burnout["duration"] -= 1

        if self.db.elemental_fury["active"]:
            if self.db.elemental_fury["duration"] == 1:
                self.db.elemental_fury["active"] = False
                deactivateMsg = (
                    f"|CThe energy around you dissipates, leaving you feeling drained."
                )
                self.location.msg_contents(deactivateMsg, from_obj=self)
            self.db.elemental_fury["duration"] -= 1

        total_fp_regen = base_fp_regen + int(bonus_fp)
        if self.traits.hp and self.traits.fp and self.traits.ep:
            self.traits.hp.current += base_regen
            self.traits.fp.current += total_fp_regen
            self.traits.ep.current += base_ep_regen
        print(f"{self} EE Tick: {self.traits.hp.current}")

    def get_display_name(self, looker, **kwargs):
        """
        Adds color to the display name.
        """
        name = super().get_display_name(looker, **kwargs)
        if looker == self:
            # special color for our own name
            return f"|c{name}|n"
        return f"|g{name}|n"

    # property to mimic weapons
    @property
    def speed(self):
        weapon = self.db.natural_weapon
        return weapon.get("speed", 3)

    def at_wield(self, weapon, **kwargs):
        self.msg(f"You cannot wield weapons.")
        return False

    def attack(self, target, weapon, **kwargs):
        weapon = EarthAttack()

        # can't attack if we're fleeing!
        if self.db.fleeing:
            return
        # make sure that we can use our chosen weapon
        if not (hasattr(weapon, "at_pre_attack") and hasattr(weapon, "at_attack")):
            return
        if not weapon.at_pre_attack(self):
            # the method handles its own error messaging
            return

        # if target is not set, use stored target
        if not target:
            # make sure there's a stored target
            if not (target := self.db.combat_target):
                self.msg("You cannot attack nothing.")
                return

        if target.location != self.location:
            self.msg("You don't see your target.")
            return

        if not self.in_combat:
            self.enter_combat(target)
            target.enter_combat(self)
            return

        weapon.at_attack(self, target)

        status = self.get_display_status(target)
        self.msg(prompt=status)

        # check if we have auto-attack in settings
        if self.account and (settings := self.account.db.settings):
            if settings.get("auto attack") and (speed := weapon.speed):
                # queue up next attack; use None for target to reference stored target on execution
                delay(speed + 1, self.attack, None, weapon, persistent=True)

    def at_damage(self, attacker, damage, damage_type=None):
        """
        Apply damage, after taking into account damage resistances.
        """
        glvl = self.db.guild_level
        con = self.traits.con.value
        hp = self.traits.hp.current
        hpmax = self.traits.hp.base
        mineral_fort = self.db.skills.get("mineral fortification", 1)
        rock_solid_defense = self.db.skills.get("rock solid defense", 1)
        stone_mastery = self.db.skills.get("stone mastery", 1)
        earth_resonance = self.db.skills.get("earth resonance", 1)
        hp_percentage = hp / hpmax
        reaction = int(self.db.reaction_percentage or 1) / 100

        percentage_reduction = 0
        flat_reduction = 0
        base_damage = damage
        # Apply (worn) defense reduction
        damage -= self.defense(damage_type)

        if self.tags.get("meditating", category="status"):
            self.tags.remove("meditating", category="status")

        # Flat damage reduction - 50 con = 5 reduction, glvl 30 = 1.5 reduction
        flat_reduction = con * 0.1 + glvl * 0.05

        # Reduce flat reduction with elemental fury on
        if self.db.elemental_fury["active"]:
            flat_reduction -= 30

        # Additional flat reduction from earth form
        if self.db.active_form == "earth":
            earth_form_reduction = int(
                mineral_fort + rock_solid_defense + stone_mastery
            )
            flat_reduction += earth_form_reduction

        # Additional flat reduction from mountain stance
        if self.db.mountain_stance:
            flat_reduction += 10

        # Additional damage reduction from mountain stance
        if self.db.mountain_stance:
            percentage_reduction += 0.1

        # Percentage damage reduction 2% per skill level
        percentage_reduction = rock_solid_defense * 0.02

        # Additional damage reduction from earth shield
        if self.db.earth_shield["hits"] > 0:
            earth_shield_reduction = stone_mastery * 0.02 + earth_resonance * 0.03
            percentage_reduction += earth_shield_reduction
            flat_reduction += stone_mastery + earth_resonance

            if self.db.earth_shield["hits"] == 1:
                deactivateMsg = f"|CYour form loses its shimmer as the protective shield of stone dissipates."
                self.location.msg_contents(deactivateMsg, from_obj=self)

            self.db.earth_shield["hits"] -= 1
            self.msg(f"|cYour earth shield blocks a lot of damage!|n")

        # Apply randomized flat reduction
        damage -= uniform(flat_reduction / 2, flat_reduction)

        # Apply percentage reduction
        damage *= 1 - percentage_reduction

        # Apply defense reduction
        damage -= self.defense(damage_type)

        # apply mineral_fortification after defense if it's enabled
        if damage_type in ("blunt", "edged") and self.db.stone_skin:
            stone_skin_absorbed = (
                (mineral_fort * 3)
                + uniform(0, glvl / 2)
                + uniform(0, 30)
                + (self.traits.con.value * 0.20)
            )
            damage -= int(stone_skin_absorbed)
            self.traits.ep.current -= 1
        else:
            stone_skin_absorbed = int(
                (mineral_fort * 3)
                + uniform(0, glvl / 2)
                + uniform(0, 30)
                + (self.traits.con.value * 0.20) / 2
            )
            self.traits.ep.current -= 2

        # randomize damage
        damage = uniform(damage / 2, damage)

        # Minimum chip damage of 1 or 3% of base damage, 50% of the time
        min_damage = math.ceil(base_damage * 0.03)

        if damage < min_damage and randint(1, 100) <= 50:
            damage = max(damage, min_damage)

        damage = max(damage, 0)
        # Apply the damage to the character
        self.traits.hp.current -= int(damage)

        # Get the attack emote
        attacker.get_npc_attack_emote(self, damage, self.get_display_name(self))

        # Check if the character is below the reaction percentage
        if hp_percentage < reaction and glvl > 3:
            self.msg(f"|cYou are below {reaction*100}% health!|n")
            self.execute_cmd("terran restoration")

        if hp <= 0:
            self.tags.add("unconscious", category="status")
            self.tags.add("lying down", category="status")
            self.msg(
                "You fall unconscious. You can |wrespawn|n or wait to be |wrevive|nd."
            )
            if self.in_combat:
                combat = self.location.scripts.get("combat")[0]
                combat.remove_combatant(self)
