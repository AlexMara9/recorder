from abc import ABC, abstractmethod

class IModule(ABC):
    
    @abstractmethod
    def on_state_change(self, state) -> None:
        """Handle state change."""
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """Shutdown the module."""
        pass