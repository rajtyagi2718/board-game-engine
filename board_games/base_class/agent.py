class Agent:

    def __init__(self, name, search):
        self._name = name
        self._search = search
        self._record = dict.fromkeys('wins losses draws'.split(), 0)

    def __repr__(self):
        """Return name - search - (record).

        Return
        ------
        str

        """
        return self._name + ' ' + repr(self._search) + ' ' + repr(self._record)

    def clear(self):
        """Reset to initial state."""
        self._search.clear()
        self._record = dict.fromkeys(self_record, 0)
