# in a module tests.py somewhere i your game dir
import unittest

from evennia import create_object
from evennia.commands.default.tests import EvenniaCommandTest
from commands import command as mycommand

# the function we want to test
from .earth_elemental_commands import CmdMudPatch
from typeclasses.elementalguild.earth_elemental_commands import EarthElementalCmdSet
from typeclasses.rooms import CmdJoinElementals


class TestObj(unittest.TestCase):
    "This tests earth elemental commands"
    player = create_object("typeclasses.characters.Character", key="TestPlayer")
    player.swap_typeclass(
        "typeclasses.elementalguild.earth_elemental.EarthElemental",
        clean_attributes=False,
    )
    player.cmdset.add(EarthElementalCmdSet, persistent=True)

    def test_mud_patch(self):
        pl = self.player
        cur = pl.traits.hp.current
        print(f"player: {self.player} {cur}")
        pl.traits.hp.current = 1
        print(f"player 2: {self.player} {pl.traits.hp.current}")
        amt = yield from pl.execute_cmd("mud patch")
        print(f"player 3: {amt} {pl.traits.hp.current}")
        actual_return = self.player.traits.hp.current

        expected_return = self.player.traits.hp.current == 10
        self.assertEqual(expected_return, actual_return)

    def test_return_value(self):
        """test method. Makes sure return value is as expected."""
        print(f"player: {self.player} {self.player.traits.hp.current}")
        # actual_return = myfunc(self.obj)
        # expected_return = "This is the good object 'mytestobject'."
        # test
        # self.assertEqual(expected_return, actual_return)

    # def test_alternative_call(self):
    #     """test method. Calls with a keyword argument."""
    #     actual_return = myfunc(self.obj, bad=True)
    #     expected_return = "This is the baaad object 'mytestobject'."
    #     # test
    #     self.assertEqual(expected_return, actual_return)
