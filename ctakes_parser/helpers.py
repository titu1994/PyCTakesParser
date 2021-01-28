from collections import defaultdict, OrderedDict
import pandas as pd


class BaseDataframeModule:

    def __init__(self):
        self.keys = []

    def to_dataframe(self):
        data = OrderedDict()
        keys = list(sorted(self.keys))

        for key in keys:
            data[key] = getattr(self, key)

        df = pd.DataFrame(data=data, columns=keys)
        return df

    def __repr__(self):
        repr_array = [self.__class__.__name__]
        for key in self.keys:
            datum = getattr(self, key, [])
            repr_array.append("{}: {}".format(key, repr(datum)))
        repr_array.append('\n')
        return '\n'.join(repr_array)


class ResultDataframeModule(BaseDataframeModule):
    
    def __init__(self):
        super(ResultDataframeModule, self).__init__()
        self._index = defaultdict(list)

    def insert(self, textsem=None, refsem=None, id=None, pos_start=None, pos_end=None, cui=None, negated=None,
               preferred_text=None, scheme=None, code=None, tui=None, score=None, confidence=None, uncertainty=None,
               conditional=None, generic=None, subject=None):

        for k, v in locals().items():
            if k != 'self':
                # Get a default list, or previously existing list
                # and append the new data point
                col = getattr(self, k, [])
                col.append(v)

                # Register the new column name
                if not hasattr(self, k):
                    self.keys.append(k)
                    setattr(self, k, col)

                # Update indices
                if k == 'id':
                    pos = len(getattr(self, self.keys[0])) - 1
                    self.update_index(v, pos)

    def update_val_at(self, id, col_name, val):
        positions = self.get_indices(id)

        # Ignores empty array from `None` indices
        for position in positions:
            getattr(self, col_name)[position] = val

    def get_indices(self, id):
        # Ignore None ids
        if id is None:
            return []
        else:
            return self._index[id]

    def update_index(self, id, pos):
        if id is not None:
            self._index[id].append(pos)


class PositionDataframeModule(BaseDataframeModule):

    def insert(self, pos_start=None, pos_end=None, part_of_speech=None, text=None):
        for k, v in locals().items():
            if k != 'self':
                # Get a default list, or previously existing list
                # and append the new data point
                col = getattr(self, k, [])
                col.append(v)

                # Register the new column name
                if not hasattr(self, k):
                    self.keys.append(k)
                    setattr(self, k, col)
