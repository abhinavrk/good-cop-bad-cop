from gcbc.core.core_data import Player
from gcbc.operators.equipment.blackmail import Blackmail
from gcbc.operators.equipment.defibrillator import Defibrillator
from gcbc.operators.equipment.polygraph import Polygraph
from gcbc.operators.equipment.swap import Swap
from gcbc.operators.equipment.taser import Taser


class Equipments:

    def blackmail(self, user: Player, target: Player) -> Blackmail:
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
        return Blackmail(user, target)

    def defibrillator(self, user: Player, target: Player) -> Defibrillator:
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
        return Defibrillator(user, target)

    def polygraph(self, user: Player, target: Player) -> Polygraph:
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
        return Polygraph(user, target)

    def swap(
        self, user: Player, playerA: Player, cardA: int, playerB: Player, cardB: int
    ) -> Swap:
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
        return Swap(user, playerA, cardA, playerB, cardB)

    def taser(self, user: Player, target: Player, aimed_at: Player) -> Taser:
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
        return Taser(user, target, aimed_at)