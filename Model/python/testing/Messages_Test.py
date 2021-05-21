import constants
from Messages import Messages

def add():
    msgs = Messages(10)

    assert(len(msgs.bitlist) == 0)
    assert(len(msgs.times.queue) == 0)

    msgs.add("1", 0)

    assert(len(msgs.bitlist) == 1)
    assert(len(msgs.times.queue) == 1)

def update():
    msgs = Messages(10)

    # should contain 1 at time 0
    msgs.update([1], 0)

    # should contain 1 at time 0 and 2, 3 at time TIME_STEP
    msgs.update([1, 2, 3], constants.TIME_STEP)

    assert(1 in msgs.bitlist and 2 in msgs.bitlist and 3 in msgs.bitlist)
    assert((0, 1) in msgs.times.queue and (100, 2) in msgs.times.queue and (100, 3) in msgs.times.queue)

def clean():
    msgs = Messages(10)

    time = 0

    msgs.add("1", time)
    msgs.add("2", time)

    for _ in range(5 * 60 * 1000 // constants.TIME_STEP - 1):
        time += constants.TIME_STEP
        msgs.clean(time)

    assert(len(msgs.bitlist) != 0)

    time += constants.TIME_STEP
    msgs.clean(time)

    assert(len(msgs.bitlist) == 0)

def compare():
    time = 0

    msgs1 = Messages(10)
    msgs2 = Messages(10)

    msgs1.add("1", time)
    msgs1.add("2", time)

    msgs2.add("2", time)
    msgs2.add("3", time)

    assert(msgs2.compare(msgs1.bitlist)[0] == 28515) # hash(1)
