from google.adk.plugins import BasePlugin


class RequestCountPlugin(BasePlugin):
    """Counts every user message across all agents in the runner."""

    def __init__(self):
        super().__init__(name="request_counter")
        self.count = 0

    async def on_user_message(self, invocation_context, user_message):
        self.count += 1
        preview = ""
        if hasattr(user_message, "parts") and user_message.parts:
            for part in user_message.parts:
                if hasattr(part, "text") and part.text:
                    preview = part.text[:50]
                    break
        print(f"[Plugin] Request #{self.count}: '{preview}'")
        return None
