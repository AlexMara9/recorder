from imodule import IModule
from tul.tul_node import AsState
from jtop import jtop
from enum import IntEnum

class JtopLogger(IModule):
    def __init__(self):
        super().__init__()

        # ====== config ======
        self._jtop_timer = self.create_timer(1.0, self.jtop_timer_callback)
        self._jtop_timer.cancel()  # Start with timer stopped

        # ====== var ======
        self._current_state = None
        self._jetson = None

    def jtop_timer_callback(self):
        if self._jetson.ok():
            stats = self._jetson.stats
            self.get_logger().info(f"Jetson Stats: {stats}")
        else:
            self.get_logger().error("Error while fetching Jetson stats")

    def next_state(self, state) -> IntEnum:
        return self._current_state + 1 if self._current_state is not None else AsState.IDLE
    
    def next_state_is_correct(self, state) -> bool:
        return state == self.next_state(state)

    def on_state_change(self, state) -> None:
        match state:
            case AsState.IDLE:
                if not self.next_state_is_correct(state): return
                self._current_state = state

            case AsState.CHECKING:
                if not self.next_state_is_correct(state): return
                self._current_state = state
                try:
                    self._jetson = jtop()
                    self._jetson.start()
                    self.get_logger().info("Successfully connected to Jetson hardware monitor.")
                except Exception as e:
                    self.get_logger().error(f"Failed to connect to Jetson hardware monitor: {e}")
            
            case AsState.READY:
                if not self.next_state_is_correct(state): return
                self._current_state = state

            case AsState.DRIVE:
                if not self.next_state_is_correct(state): return
                self._current_state = state
                self._jtop_timer.start()    # Start logging

            case AsState.FINISH:
                if not self.next_state_is_correct(state): return
                self._current_state = state

            case AsState.EMERGENCY:
                pass
            case _:
                pass

    def shutdown(self) -> None:
        if self._jetson:
            self._jetson.stop()
            self._jtop_timer.cancel()