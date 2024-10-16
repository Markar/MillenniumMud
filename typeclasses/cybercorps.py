from random import randint, uniform, choice
from evennia.utils import delay, iter_to_str
from evennia import TICKER_HANDLER as tickerhandler
from typeclasses.characters import PlayerCharacter
from typeclasses.cybercorpsguild.attack_emotes import AttackEmotes
from typeclasses.utils import get_article, get_display_name, geHealthStatus
from typeclasses.cybercorpsguild.cybercorps_commands import CybercorpsCmdSet
from typeclasses.cybercorpsguild.cyber_implants import (
    CybercorpsImplantCmdSet,
)
from typeclasses.cybercorpsguild.cybercorps_wares import (
    HandRazors,
)
from typeclasses.cybercorpsguild.cybercorps_wares import CybercorpsWaresCmdSet


class Cybercorps(PlayerCharacter):
    """
    The base typeclass for non-player characters, implementing behavioral AI.
    """

    def at_object_creation(self):
        self.cmdset.add(CybercorpsCmdSet, persistent=True)
        self.cmdset.add(CybercorpsWaresCmdSet, persistent=True)
        self.cmdset.add(CybercorpsImplantCmdSet, persistent=True)
        super().at_object_creation()
        con_increase_amount = 20
        int_increase_amount = 5
        self.db.con_increase_amount = con_increase_amount
        self.db.int_increase_amount = int_increase_amount
        self.db.con_bonus = 0
        self.traits.hp.base = 50 + (
            con_increase_amount * (self.traits.con.value + self.db.con_bonus)
        )
        self.traits.fp.base = 50 + (int_increase_amount * self.traits.int.value)

        self.db.guild_level = 1
        self.db.gxp = 0
        self.db.skill_gxp = 0
        self.db.title = "the New Recruit"

        self.db.natural_weapon = {
            "name": "hand_razors",
            "damage_type": "edged",
            "damage": 12,
            "speed": 3,
            "energy_cost": 10,
        }
        self.db.guild = "cybercorps"
        self.db.subguild = "none"
        self.db._wielded = {"left": None, "right": None}
        self.db.hpregen = 1
        self.db.fpregen = 1
        self.db.epregen = 1
        self.db.strategy = "melee"
        self.db.skills = {
            "standard weapons": 1,
            "energy weapons": 1,
            "heavy weapons": 1,
            "cybernetic enhancements": 1,
            "security services": 1,
            "biotech research": 1,
            "energy solutions": 1,
        }
        self.db.melee_weapon = HandRazors()
        self.db.ranged_weapon = None
        self.db.adaptive_armor = False
        self.db.nano_reinforced_skeleton = False
        self.db.nrs_amount = 0
        # list of owned wares
        self.db.wares = ["hand razors"]
        self.db.docwagon = {"count": 0, "max": 0}
        self.db.implants = []
        self.db.platelet_factory_active = False
        self.db.adrenaline_boost = {"active": False, "duration": 0}

        tickerhandler.add(
            interval=6, callback=self.at_tick, idstring=f"{self}-regen", persistent=True
        )
        tickerhandler.add(
            interval=60 * 5,
            callback=self.at_docwagon_tick,
            idstring=f"{self}-superpower",
            persistent=True,
        )

    def kickstart(self):
        self.msg("Kickstarting heartbeat")
        tickerhandler.add(
            interval=6, callback=self.at_tick, idstring=f"{self}-regen", persistent=True
        )
        tickerhandler.add(
            interval=60 * 5,
            callback=self.at_docwagon_tick,
            idstring=f"{self}-superpower",
            persistent=True,
        )

    def at_tick(self):
        base_regen = self.db.hpregen
        base_ep_regen = self.db.epregen
        base_fp_regen = self.db.fpregen
        biotech_research = self.db.skills.get("biotech research", 1)
        energy_solutions = self.db.skills.get("energy solutions", 1)
        adaptive_armor = getattr(self.db, "adaptive_armor", False)
        implants = getattr(self.db, "implants", False)
        platelet_factory_active = getattr(self.db, "platelet_factory_active", False)

        bonus_hp = 0
        bonus_fp = 0
        bonus_ep = 0

        bonus_ep += int(uniform(energy_solutions * 0.2, energy_solutions * 0.3))  # 0-3

        if platelet_factory_active:
            bonus_hp += 1 + biotech_research

        if adaptive_armor and self.traits.ep.current < 6:
            bonus_ep -= 5
            self.db.adaptive_armor = False
            self.msg(f"|CAs your energy runs out, your adaptive armor powers down.|n")

        total_hp_regen = base_regen + int(bonus_hp)
        total_fp_regen = base_fp_regen + int(bonus_fp)
        total_ep_regen = base_ep_regen + int(bonus_ep)

        self.traits.hp.current += total_hp_regen
        self.traits.fp.current += total_fp_regen
        self.traits.ep.current += total_ep_regen

    def at_docwagon_tick(self):
        """
        Regenerate docwagon basic service calls.
        """
        if self.db.guild_level <= 7:
            return
        self.msg(
            f"|CYou can now call for additional emergency services at any time. Stay safe out there!"
        )

        self.db.docwagon["count"] = self.db.docwagon["max"]

    # property to mimic weapons
    @property
    def speed(self):
        weapon = self.db.natural_weapon
        return weapon.get("speed", 3)

    def get_player_attack_hit_message(self, attacker, dam, tn, emote="hand_razors"):
        """
        Get the hit message based on the damage dealt. This is the elemental's
        version of the method, defaulting to the earth elemental version but
        should be overridden by subguilds.

        ex:
            f"{color}$You() hurl a handful of dirt, but it scatters harmlessly.",
        """

        # self.msg(f"attacker {attacker} dam {dam} tn {tn} emote {emote}")
        msgs = AttackEmotes.get_emote(attacker, emote, tn, which="left")

        if dam <= 0:
            to_me = msgs[0]
        elif 1 <= dam <= 5:
            to_me = msgs[1]
        elif 6 <= dam <= 12:
            to_me = msgs[2]
        elif 13 <= dam <= 20:
            to_me = msgs[3]
        elif 21 <= dam <= 30:
            to_me = msgs[4]
        elif 31 <= dam <= 50:
            to_me = msgs[5]
        elif 51 <= dam <= 80:
            to_me = msgs[6]
        elif 81 <= dam <= 140:
            to_me = msgs[7]
        elif 141 <= dam <= 225:
            to_me = msgs[8]
        elif 225 <= dam <= 325:
            to_me = msgs[9]
        else:
            to_me = msgs[10]

        to_me = f"{to_me} ({dam})"
        self.location.msg_contents(to_me, from_obj=self)

        return to_me

    def enter_combat(self, target, **kwargs):
        """
        initiate combat against another character
        """
        if weapons := self.wielding:
            weapon = weapons[0]
        else:
            weapon = self

        if target is not None:
            self.at_emote("$conj(charges) at {target}!", mapping={"target": target})
        location = self.location

        if not (combat_script := location.scripts.get("combat")):
            # there's no combat instance; start one
            from typeclasses.scripts import CombatScript

            location.scripts.add(CombatScript, key="combat")
            combat_script = location.scripts.get("combat")

        combat_script = combat_script[0]
        self.db.combat_target = target

        # adding a combatant to combat just returns True if they're already there, so this is safe
        if not combat_script.add_combatant(self, enemy=target):
            return
        self.attack(target, weapon)

    def get_combat_display_status(self, looker, **kwargs):
        # This is a wrapper for the get_display_status method that adds a cooldown
        # to prevent spamming the status display due to calling attack every second.

        if not self.cooldowns.ready("combat_display_status"):
            return
        print("getting combat  display status")
        msg = self.get_display_status(looker, **kwargs)
        self.msg(msg)
        self.cooldowns.add("combat_display_status", 3)

    def get_display_status(self, looker, **kwargs):
        """
        Returns a quick view of the current status of this character
        """
        chunks = []
        print("getting display status")

        # add resource levels
        hp = int(self.traits.hp.current)
        hpmax = int(self.traits.hp.base)
        fp = int(self.traits.fp.current)
        fpmax = int(self.traits.fp.base)
        ep = int(self.traits.ep.current)
        epmax = int(self.traits.ep.base)
        docwagon_count = self.db.docwagon["count"]
        docwagon_max = self.db.docwagon["max"]
        adaptive_armor = getattr(self.db, "adaptive_armor", False)
        platelet_factory_active = getattr(self.db, "platelet_factory_active", False)
        adrenaline_boost = getattr(self.db, "adrenaline_boost", {})
        adrenaline_boost_active = adrenaline_boost.get("active", False)
        nrs = getattr(self.db, "nano_reinforced_skeleton", False)

        chunks.append(
            f"|gHealth: |G{hp}/{hpmax}|g Focus: |G{fp}/{fpmax}|g Energy: |G{ep}/{epmax}|g"
        )
        if docwagon_max:
            chunks.append(f"|gDocWagon: |G{docwagon_count}/{docwagon_max}|g")
        if adaptive_armor:
            chunks.append(f"|gAA")
        if platelet_factory_active:
            chunks.append(f"|gPF")
        if adrenaline_boost_active:
            chunks.append(f"|gAB")
        if nrs:
            chunks.append(f"|gNRS")

        if looker != self:
            chunks.append(f"|gE: |G{looker.get_display_name(self, **kwargs)}")
            hpPct = looker.traits.hp.current / looker.db.hpmax
            status = geHealthStatus(self, hpPct)
            chunks.append(f"|gH: |G{status}")
            if self.key == "Markar":
                chunks.append(f"{looker.traits.hp.current} / {looker.db.hpmax}")

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

        return " - ".join(chunks)

    # region Attack
    def attack(self, target, weapon, **kwargs):
        weapon_delay = 1
        if not self.in_combat:
            self.enter_combat(target)
            if target:
                target.enter_combat(self)
            return

        # can't attack if we're fleeing!
        if self.db.fleeing:
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

        melee_weapon = self.db.melee_weapon
        ranged_weapon = self.db.ranged_weapon

        if melee_weapon:
            melee_weapon.at_attack(self, target)

        if ranged_weapon:
            ranged_weapon.at_attack(self, target)

        status = self.get_combat_display_status(target)

        # check if we have auto-attack in settings
        if self.account and (settings := self.account.db.settings):
            if settings.get("auto attack") and (speed := weapon.speed):
                # queue up next attack; use None for target to reference stored target on execution
                delay(weapon_delay, self.attack, None, weapon, persistent=True)

    # region At_damage
    def at_damage(self, attacker, damage, damage_type=None):
        """
        Apply damage, after taking into account damage resistances.
        """
        glvl = self.db.guild_level
        con = self.traits.con.value
        hp = self.traits.hp.current
        hpmax = self.traits.hp.base
        hp_percentage = hp / hpmax
        reaction = int(self.db.reaction_percentage or 1) / 100
        cybernetic_enhancements = self.db.skills.get("cybernetic enhancements", 1)
        security_services = self.db.skills.get("security services", 1)
        biotech_research = self.db.skills.get("biotech research", 1)
        energy_solutions = self.db.skills.get("energy solutions", 1)

        percentage_reduction = 0
        flat_reduction = 0
        flat_reduction_cap = 0

        if self.db.guild_level < 5:
            flat_reduction_cap = 5
        elif self.db.guild_level < 10:
            flat_reduction_cap = 15
        elif self.db.guild_level < 15:
            flat_reduction_cap = 30
        elif self.db.guild_level < 20:
            flat_reduction_cap = 60
        elif self.db.guild_level < 25:
            flat_reduction_cap = 150

        # Flat damage reduction - 50 con = 5 reduction, glvl 30 = 1.5 reduction
        flat_reduction = con * 0.1 + glvl * 0.05

        # Additional flat reduction from adaptive armor
        if self.db.adaptive_armor:
            adaptive_armor_reduction = int(
                con * 0.1 + glvl * 0.1 + cybernetic_enhancements
            )
            percentage_reduction += cybernetic_enhancements / 100
            flat_reduction += adaptive_armor_reduction
            self.traits.ep.current -= 1

        if self.db.nano_reinforced_skeleton:
            percentage_reduction += 0.02 + cybernetic_enhancements / 200

        # Additional flat reduction from mountain stance
        # if self.db.mountain_stance:
        #     flat_reduction += 10

        # Additional damage reduction from mountain stance
        # if self.db.mountain_stance:
        #     percentage_reduction += 0.1

        # Percentage damage reduction 2% per skill level
        # percentage_reduction = rock_solid_defense * 0.02

        # Additional damage reduction from earth shield
        # if self.db.earth_shield["hits"] > 0:
        #     earth_shield_reduction = stone_mastery * 0.02 + earth_resonance * 0.03
        #     percentage_reduction += earth_shield_reduction
        #     flat_reduction += stone_mastery + earth_resonance

        #     if self.db.earth_shield["hits"] == 1:
        #         deactivateMsg = f"|C$Your() form loses its shimmer as the protective shield of stone dissipates."
        #         self.location.msg_contents(deactivateMsg, from_obj=self)

        #     self.db.earth_shield["hits"] -= 1
        #     self.msg(f"|cYour earth shield blocks a lot of damage!|n")

        # Apply randomized flat reduction

        # Apply (worn) defense reduction
        armor = self.defense(damage_type)
        flat_reduction += int(uniform(armor * 0.25, armor))

        # Apply the flat reduction cap
        if flat_reduction > flat_reduction_cap:
            flat_reduction = flat_reduction_cap

        # Apply the flat reduction
        damage -= uniform(flat_reduction / 2, flat_reduction)

        # Apply percentage reduction
        damage *= 1 - percentage_reduction

        # randomize damage
        damage = uniform(damage / 2, damage)

        # Make sure damage is an integer, similar to floor rounding
        damage = int(damage)

        # Ensure damage doesn't go below zero
        damage = max(damage, 0)

        # Apply the damage to the character
        self.traits.hp.current -= damage

        # Get the attack emote
        attacker.get_npc_attack_emote(self, damage, self.get_display_name(self))

        # Check if the character is below the reaction percentage
        if hp_percentage < reaction and self.db.docwagon["count"] > 0:
            self.msg(f"|cYou are below {reaction*100}% health!|n")
            self.execute_cmd("docwagon revive")

        if hp <= 0:
            self.tags.add("unconscious", category="status")
            self.tags.add("lying down", category="status")
            self.msg(
                "You fall unconscious. You can |wrespawn|n or wait to be |wrevive|nd."
            )
            if self.in_combat:
                combat = self.location.scripts.get("combat")[0]
                combat.remove_combatant(self)

    def can_wear(self, item):
        """
        Check if the character can wear an item
        """
        armor = getattr(item.db, "armor", False)
        type = getattr(item.db, "type", False)
        allowed_types = ["light", "medium", "heavy"]

        if not item:
            return False

        if not item.db.clothing_type:
            self.msg(f"{item} is not wearable.")
            return False

        if armor and type not in allowed_types:
            self.msg(f"You can't wear that kind of armor.")
            return False

        return True
