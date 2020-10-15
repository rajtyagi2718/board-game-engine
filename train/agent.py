from agents.heursitic import HeuristicAgent
from logs.log import get_logger

LOGGER = get_logger(__name__)

WEIGHTS_PATH = Path('models/weights/')

class TrainAgent(HeuristicAgent):

    def __init__(self, name):
        super().__init__(name, WEIGHTS_PATH)
