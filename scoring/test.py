class Test:
    def __init__(self):
        self.v = 1

    @property
    def v(self):
        print(self.v)
        return self.v

    @v.setter
    def v(self, *args, **kwargs):
        print("calling some_property setter({0},{1},{2})".format(self, args, kwargs))
        self.v = args[0]


t = Test()
t.v = 2
print(t.v)

