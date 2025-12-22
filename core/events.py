class EventBus:
    def __init__(self):
        self._listeners = {}

    def on(self, event, callback):
        if event not in self._listeners:
            self._listeners[event] = []
        self._listeners[event].append(callback)

    def emit(self, event, *args, **kwargs):
        for callback in self._listeners.get(event, []):
            callback(*args, **kwargs)