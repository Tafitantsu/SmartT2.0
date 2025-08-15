import time
import random

class PetriNet:
    def __init__(self):
        # V=Green, J=Yellow, R=Red
        self.places = {
            "NS_V": 1, "NS_J": 0, "NS_R": 0,
            "EW_V": 0, "EW_J": 0, "EW_R": 1,
            "P_NS_V": 0, "P_NS_R": 1,
            "P_EW_V": 0, "P_EW_R": 1,
            "D_P_NS": 0, "D_P_EW": 0,
            "Q_NS": 0, "Q_EW": 0, # Queues start at 0
            "ALL_R": 0,
        }

        self.state = "NS_V"
        # Fixed timers as per requirements
        self.state_timers = {
            "NS_V": 10, # Priority road green
            "NS_J": 2,  # Yellow
            "EW_V": 5,  # Non-priority road green
            "EW_J": 2,  # Yellow
            "ALL_R": 2, # All-red transition (used for night mode off-phase)
            "FLASH_J": 2 # Flashing yellow for night mode
        }

        self.night_mode = False
        self.last_main_state = "EW" # Start assuming we just finished an EW cycle to go to NS_V first
        self.last_state_change_time = time.time()
        self.current_timer_duration = self._get_new_timer_duration()

    def toggle_night_mode(self):
        """Toggles the night mode on and off."""
        self.night_mode = not self.night_mode
        print(f"Night mode toggled to: {self.night_mode}")
        if self.night_mode:
            # When entering night mode, go to a safe state first
            self._transition_to("ALL_R")
        else:
            # When exiting night mode, go to a safe state before starting day cycle
            self._transition_to("ALL_R")

    def _get_new_timer_duration(self):
        """Returns the fixed duration for the current state."""
        return self.state_timers.get(self.state, 1)

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
        """Handles the logic for transitioning to a new state."""
        self.state = new_state

        # Reset all light places to a known-safe state (all red)
        for k in ["NS_V", "NS_J", "EW_V", "EW_J", "ALL_R", "P_NS_V", "P_EW_V"]:
            self.places[k] = 0
        self.places["NS_R"] = 1
        self.places["EW_R"] = 1
        self.places["P_NS_R"] = 1
        self.places["P_EW_R"] = 1

        # Set new light places based on the new state
        if new_state == "NS_V":
            self.places["NS_V"] = 1
            self.places["NS_R"] = 0
            # Pedestrians on EW can cross, consuming the demand
            self.places["P_EW_V"] = 1
            self.places["P_EW_R"] = 0
            self.places["D_P_EW"] = 0
        elif new_state == "NS_J":
            self.places["NS_J"] = 1
            self.places["NS_R"] = 0
            self.last_main_state = "NS" # Record that we came from the NS cycle
            # If the change was triggered by a pedestrian, consume the demand now
            if self.places["D_P_NS"] == 1:
                self.places["D_P_NS"] = 0
        elif new_state == "EW_V":
            self.places["EW_V"] = 1
            self.places["EW_R"] = 0
            # Pedestrians on NS can cross, consuming the demand
            self.places["P_NS_V"] = 1
            self.places["P_NS_R"] = 0
            self.places["D_P_NS"] = 0
        elif new_state == "EW_J":
            self.places["EW_J"] = 1
            self.places["EW_R"] = 0
            self.last_main_state = "EW" # Record that we came from the EW cycle
        elif new_state == "ALL_R":
            self.places["ALL_R"] = 1
        elif new_state == "FLASH_J":
            # In night mode, both yellow lights will be managed by the run_step
            self.places["NS_J"] = 1
            self.places["EW_J"] = 1
            self.places["NS_R"] = 0 # Yellow flashing is not a red light
            self.places["EW_R"] = 0

        self.last_state_change_time = time.time()
        self.current_timer_duration = self._get_new_timer_duration()

    def run_step(self):
        """The main simulation tick, to be called periodically."""
        # Car queue simulation
        if self.places["NS_V"] == 1 and self.places["Q_NS"] > 0:
            self.places["Q_NS"] = max(0, self.places["Q_NS"] - 1) # One car passes
        if self.places["EW_V"] == 1 and self.places["Q_EW"] > 0:
            self.places["Q_EW"] = max(0, self.places["Q_EW"] - 1)

        # Check if it's time to transition
        time_elapsed = time.time() - self.last_state_change_time
        if time_elapsed < self.current_timer_duration:
            return # Not time yet

        # --- State Transition Logic ---
        if self.night_mode:
            if self.state == "ALL_R":
                self._transition_to("FLASH_J")
            elif self.state == "FLASH_J":
                self._transition_to("ALL_R")
            # If not in a standard night mode state, force it to ALL_R
            elif self.state not in ["ALL_R", "FLASH_J"]:
                self._transition_to("ALL_R")
        else:
            # --- Day Mode State Logic ---
            state = self.state
            time_elapsed = time.time() - self.last_state_change_time
            timer_expired = time_elapsed >= self.current_timer_duration

            if state == "NS_V":
                # Priority road stays green by default.
                # It will only change if a condition is met AND min green time has passed.
                min_green_time_passed = time_elapsed >= self.current_timer_duration
                car_waiting_ew = self.places["Q_EW"] > 0
                pedestrian_request_ns = self.places["D_P_NS"] == 1

                if min_green_time_passed and (car_waiting_ew or pedestrian_request_ns):
                    self._transition_to("NS_J")
            elif state == "NS_J":
                if timer_expired:
                    self._transition_to("ALL_R")
            elif state == "EW_V":
                if timer_expired:
                    self._transition_to("EW_J")
            elif state == "EW_J":
                if timer_expired:
                    self._transition_to("ALL_R")
            elif state == "ALL_R":
                if timer_expired:
                    if self.last_main_state == "NS":
                        self._transition_to("EW_V") # Go to non-priority road
                    else: # last_main_state == "EW"
                        self._transition_to("NS_V") # Return to priority road
            # If system is in a weird state during day mode, reset it safely
            else:
                self._transition_to("ALL_R")
