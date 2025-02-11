class HonerIn:
    def __iter__(self):
        def iterator():
            pass

        return iterator()

    @property
    def winner(self):
        return self.vals[0]


def hone_in():
    honer_in = HonerIn()

    for _ in honer_in:
        pass

    return honer_in.winner
