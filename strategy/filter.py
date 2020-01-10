class SessionFilter(object):
    def __init__(self, data):
        pass

    def __call__(self, data):
        if data.p.sessionstart <= data.datetime.time() <= data.p.sessionend:
            # bar is in the session
            return False  # tell outer data loop the bar can be processed

        # bar outside of the regular session times
        data.backwards()  # remove bar from data stack
        return True  # tell outer data loop to fetch a new bar