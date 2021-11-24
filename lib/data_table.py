from lib.check_import import check_import
from lib.code import get_random_code

check_import('numpy')
from numpy import ceil, floor


class DataTable:
    """
        This class is for optimization and speed up the program the way it optimization
        and speed up is by putting the data in the table(chunk) so when reading the data
        it will be faster if you know the position of the data.

        For example if you have a big space in your game then you can use this class to
        save the player, object, etc. was there position in the space then you don't
        need to run a big for loop in your program so the program will be optimization
        and speed up when running
    """

    def __init__(self, width, height, size=25, offset_x=0, offset_y=0):
        table = {}
        for x in range(-offset_x, int(ceil(width / size)) + offset_x):
            table[x] = {}
            for y in range(-offset_y, int(ceil(height / size)) + offset_y):
                table[x][y] = {}

        self.size = size
        self.table = table

    # update any object in any position
    def update(self, x, y, data, data_id=None):
        if data_id is None:
            data_id = get_random_code()
        else:
            self.delete(x, y, data_id)

        x = round(x / self.size)
        y = round(y / self.size)
        try:
            self.table[x][y][data_id] = data
            return data_id
        except:
            pass

    # delete any object in any position
    def delete(self, x, y, data_id):
        x = round(x / self.size)
        y = round(y / self.size)
        for i in range(-1, 2):
            for j in range(-1, 2):
                try:
                    del self.table[x + i][y + j][data_id]
                    return
                except:
                    pass

    # if the play area is huge then it will only run the area that around the screen
    def get_by_area(self, x1, y1, x2, y2, offset=0):
        data = []
        x1 = int(floor((x1 - offset) / self.size))
        y1 = int(floor((y1 - offset) / self.size))
        x2 = int(ceil((x2 + offset) / self.size))
        y2 = int(ceil((y2 + offset) / self.size))
        for x in range(x1, x2):
            for y in range(y1, y2):
                try:
                    data += [self.table[x][y][data_id] for data_id in self.table[x][y]]
                except:
                    pass

        return data

    # load the area according to the player position
    def get_by_pos(self, x, y, size=1):
        data = []
        x = round(x / self.size)
        y = round(y / self.size)
        for i in range(-size, 1 + size):
            for j in range(-size, 1 + size):
                try:
                    data += [self.table[x + i][y + j][data_id] for data_id in self.table[x + i][y + j]]
                except:
                    pass
        return data

    # for for loop
    def __iter__(self):
        for x in self.table:
            yield x

    # turn class to dict
    def __getitem__(self, x):
        return self.table[x]

    # length of table
    def __len__(self):
        return len(self.table)
