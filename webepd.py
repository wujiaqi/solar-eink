from abc import ABC, abstractmethod

class EPaperDisplay(ABC):

    @abstractmethod
    def display_image(self, image):
        pass


