class Router5Port:
    """Very small router model that passes packets through unchanged."""

    def route(self, packets):
        """Return packets dictionary without modification."""
        return dict(packets)
