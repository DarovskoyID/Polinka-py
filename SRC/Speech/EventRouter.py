class EventRouter:
    def __init__(self):
        self.handlers = {}

    def on(self, event_name, handler):
        """Регистрация обработчика события"""
        self.handlers.setdefault(event_name, []).append(handler)

    def emit(self, event_name, *args):
        """Вызов всех обработчиков"""
        for handler in self.handlers.get(event_name, []):
            handler(*args)