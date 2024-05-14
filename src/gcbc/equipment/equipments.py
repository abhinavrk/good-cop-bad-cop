
from gcbc.core.core_data import Player
from gcbc.equipment.blackmail import Blackmail
from gcbc.equipment.defibrillator import Defibrillator
from gcbc.equipment.polygraph import Polygraph
from gcbc.equipment.swap import Swap
from gcbc.equipment.taser import Taser


class Equipments:

    @staticmethod
    def blackmail(user: Player, target: Player) -> Blackmail:
        """
        Create a new instance of the Blackmail class.

        Args:
            user (Player): The player who is using the blackmail card.
            target (Player): The player whose integrity cards will be flipped.

        Returns:
            Blackmail: A new instance of the Blackmail class.

        Raises:
            ValueError: If the created Blackmail instance is invalid.
        """
        blackmail = Blackmail(user, target)
        if not blackmail.is_valid(user, target):
            raise ValueError("Invalid Blackmail instance")
        return blackmail

    @staticmethod
    def defibrillator(user: Player, target: Player) -> Defibrillator:
        """
        Create a new instance of the Defibrillator class.

        Args:
            user (Player): The player who is using the defibrillator.
            target (Player): The player who is being revived.

        Returns:
            Defibrillator: A new instance of the Defibrillator class.

        Raises:
            ValueError: If the created Defibrillator instance is invalid.
        """
        defibrillator = Defibrillator(user, target)
        if not defibrillator.is_valid(user, target):
            raise ValueError("Invalid Defibrillator instance")
        return defibrillator

    @staticmethod
    def polygraph(user: Player, target: Player) -> Polygraph:
        """
        Create a new instance of the Polygraph class.

        Args:
            user (Player): The player who is using the polygraph.
            target (Player): The player whose cards will be revealed.

        Returns:
            Polygraph: A new instance of the Polygraph class.

        Raises:
            ValueError: If the created Polygraph instance is invalid.
        """
        polygraph = Polygraph(user, target)
        if not polygraph.is_valid(user, target):
            raise ValueError("Invalid Polygraph instance")
        return polygraph

    @staticmethod
    def swap(user: Player, playerA: Player, cardA: int, playerB: Player, cardB: int) -> Swap:
        """
        Create a new instance of the Swap class.

        Args:
            user (Player): The player who is using the swap card.
            playerA (Player): One of the players involved in the swap.
            cardA (int): The index of the integrity card of playerA to be swapped.
            playerB (Player): The other player involved in the swap.
            cardB (int): The index of the integrity card of playerB to be swapped.

        Returns:
            Swap: A new instance of the Swap class.

        Raises:
            ValueError: If the created Swap instance is invalid.
        """
        swap = Swap(user, playerA, cardA, playerB, cardB)
        if not swap.is_valid(user, playerA, cardA, playerB, cardB):
            raise ValueError("Invalid Swap instance")
        return swap

    @staticmethod
    def taser(user: Player, target: Player, aimed_at: Player) -> Taser:
        """
        Create a new instance of the Taser class.

        Args:
            stealer (Player): The player who is stealing the gun.
            target (Player): The player whose gun is being stolen.
            aimed_at (Player): The player who the stolen gun is aimed at.

        Returns:
            Taser: A new instance of the Taser class.

        Raises:
            ValueError: If the created Taser instance is invalid.
        """
        taser = Taser(user, target, aimed_at)
        if not taser.is_valid(user, target, aimed_at):
            raise ValueError("Invalid Taser instance")
        return taser
