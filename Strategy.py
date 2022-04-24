class Strategy:
    def __init__(self, name: str):
        self._name = name
        self._trigger = {}

    def getAction(self, trigger_type: str) -> str:
        return self._trigger[trigger_type]['action']

    def getRate(self, trigger_type: str) -> str:
        return self._trigger[trigger_type]['rate']
    
    def defRule(self, trigger_type: str, trigger_action: str, rate: float) -> None:
        if trigger_type == 'buy':
            self._trigger['buy'] = {
                'action' : trigger_action,
                'rate': rate
            }
        elif trigger_type == 'sell':
            self._trigger['sell'] = {
                'action' : trigger_action,
                'rate': rate
            }
        else:
            print("Unknown action")
            exit(3)