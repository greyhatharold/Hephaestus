import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from src.core.idea_processor import IdeaProcessor
from src.gui.gui import Layer3DGUI

def main():
    system = IdeaProcessor()
    app = Layer3DGUI(system)
    app.run()

if __name__ == "__main__":
    main()