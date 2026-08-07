"""tracking each drone by id, its location flight state and multiturn logic"""


class Drone:
    def __init__(self, drone_id: int, start_zone: str) -> None:
        self.id: int = drone_id
        # tracking zone name where the drone is now
        self.current_zone: str = start_zone
        # restricted zones takes a drone 2 turns, so this tracks how many
        # turns remaining until it lands. 0 means it lands.
        self.turns_in_transit: int = 0
        # tracks the name of the destination zone
        self.target_zone: str | None = None

    def start_transit(self, destination: str, duration: int) -> None:
        """tracks a drone status in a pathway"""
        self.target_zone = destination
        self.turns_in_transit = duration

    def update_transit(self) -> bool:
        """track each turn, true if the drone landed this turn"""
        if self.turns_in_transit > 0:
            self.turns_in_transit -= 1
            # it the countdown is zero the drone arrives
            if self.turns_in_transit == 0 and self.target_zone is not None:
                self.current_zone = self.target_zone
                self.target_zone = None
                return True
        return False
