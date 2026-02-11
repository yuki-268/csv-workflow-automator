class BaseRule:
    def apply(self, df):
        raise NotImplementedError

    def description(self):
        raise NotImplementedError

    def to_dict(self):
        raise NotImplementedError

    @staticmethod
    def from_dict(data):
        raise NotImplementedError
