import time
import random

class PetriNet:
    def __init__(self):
        # Simplified place names for clarity
        # V=Green, J=Yellow, R=Red
        self.places = {
            "NS_V": 1, "NS_J": 0, "NS_R": 0,
            "EW_V": 0, "EW_J": 0, "EW_R": 1,
            "P_NS_V": 0, "P_NS_R": 1, # Pedestrian NS
            "P_EW_V": 0, "P_EW_R": 1, # Pedestrian EW
            "D_P_NS": 0, "D_P_EW": 0, # Pedestrian Demand
            "Q_NS": 3, "Q_EW": 2,     # Vehicle Queues
            "ALL_R": 0,              # All-Red phase flag
        }

        self.state = "NS_V"  # The current state of the main traffic light cycle
        self.state_timers = {
            "NS_V": [5, 10], # Green light duration
            "NS_J": [2, 2],  # Yellow light duration
            "EW_V": [5, 10],
            "EW_J": [2, 2],
            "ALL_R": [1, 1]  # All-Red duration
        }

        self.last_state_change_time = time.time()
        self.current_timer_duration = self._get_new_timer_duration()

    def _get_new_timer_duration(self):
        t_min, t_max = self.state_timers.get(self.state, [1, 1])
        return random.uniform(t_min, t_max)

    def get_state(self):
        """Returns a JSON-friendly representation of the current state."""
        return {
            "lights": {
                "ns": "green" if self.places["NS_V"] else "yellow" if self.places["NS_J"] else "red",
                "ew": "green" if self.places["EW_V"] else "yellow" if self.places["EW_J"] else "red",
            },
            "pedestrian_lights": {
                "ns": "green" if self.places["P_NS_V"] else "red",
                "ew": "green" if self.places["P_EW_V"] else "red",
            },
            "queues": {
                "ns": round(self.places["Q_NS"]),
                "ew": round(self.places["Q_EW"]),
            },
            "demands": {
                "ns": self.places["D_P_NS"],
                "ew": self.places["D_P_EW"],
            }
        }

    def add_car(self, direction):
        if direction.upper() == "NS":
            self.places["Q_NS"] += 1
        elif direction.upper() == "EW":
            self.places["Q_EW"] += 1

    def pedestrian_request(self, direction):
        if direction.upper() == "NS":
            self.places["D_P_NS"] = 1
        elif direction.upper() == "EW":
            self.places["D_P_EW"] = 1

    def _transition_to(self, new_state):
        self.state = new_state

        # Reset all light places
        for k in ["NS_V", "NS_J", "NS_R", "EW_V", "EW_J", "EW_R", "ALL_R", "P_NS_V", "P_EW_V"]:
            self.places[k] = 0
        self.places["P_NS_R"] = 1
        self.places["P_EW_R"] = 1

        # Set new light places based on state
        if new_state == "NS_V":
            self.places["NS_V"] = 1
            self.places["EW_R"] = 1
            if self.places["D_P_EW"] == 1: # If there was a demand for EW pedestrians
                self.places["P_EW_V"] = 1
                self.places["P_EW_R"] = 0
                self.places["D_P_EW"] = 0 # Consume demand
        elif new_state == "NS_J":
            self.places["NS_J"] = 1
            self.places["EW_R"] = 1
        elif new_state == "EW_V":
            self.places["EW_V"] = 1
            self.places["NS_R"] = 1
            if self.places["D_P_NS"] == 1: # If there was a demand for NS pedestrians
                self.places["P_NS_V"] = 1
                self.places["P_NS_R"] = 0
                self.places["D_P_NS"] = 0 # Consume demand
        elif new_state == "EW_J":
            self.places["EW_J"] = 1
            self.places["NS_R"] = 1
        elif new_state == "ALL_R":
            self.places["ALL_R"] = 1
            self.places["NS_R"] = 1
            self.places["EW_R"] = 1

        self.last_state_change_time = time.time()
        self.current_timer_duration = self._get_new_timer_duration()

    def _generate_random_events(self):
        """Randomly adds new cars and pedestrian requests."""
        # Chance to add a car to NS
        if random.random() < 0.02: # 2% chance per tick
            self.add_car("NS")
        # Chance to add a car to EW
        if random.random() < 0.015: # 1.5% chance per tick
            self.add_car("EW")

        # Chance for a pedestrian request in NS
        if self.places["D_P_NS"] == 0 and random.random() < 0.005: # 0.5% chance
            self.pedestrian_request("NS")
        # Chance for a pedestrian request in EW
        if self.places["D_P_EW"] == 0 and random.random() < 0.005: # 0.5% chance
            self.pedestrian_request("EW")


    def run_step(self):
        self._generate_random_events()

        # Let cars pass if their light is green (fractional for smooth simulation)
        if self.places["NS_V"] == 1 and self.places["Q_NS"] > 0:
            self.places["Q_NS"] = max(0, self.places["Q_NS"] - 0.2)
        if self.places["EW_V"] == 1 and self.places["Q_EW"] > 0:
            self.places["Q_EW"] = max(0, self.places["Q_EW"] - 0.2)

        # Check timer
        time_elapsed = time.time() - self.last_state_change_time
        if time_elapsed < self.current_timer_duration:
            return

        # Timer expired, transition to the next state
        if self.state == "NS_V":
            self._transition_to("NS_J")
        elif self.state == "NS_J":
            self._transition_to("ALL_R")
        elif self.state == "EW_V":
            self._transition_to("EW_J")
        elif self.state == "EW_J":
            self._transition_to("ALL_R")
        elif self.state == "ALL_R":
            # Decision logic: prioritize direction with more demand (cars + pedestrians)
            # Pedestrian demand is weighted more heavily
            ns_demand = self.places["Q_NS"] + self.places["D_P_NS"] * 5
            ew_demand = self.places["Q_EW"] + self.places["D_P_EW"] * 5

            # If no demand, alternate. Start with NS.
            if ns_demand == 0 and ew_demand == 0:
                self._transition_to("NS_V")
            elif ns_demand >= ew_demand:
                self._transition_to("NS_V")
            else:
                self._transition_to("EW_V")
