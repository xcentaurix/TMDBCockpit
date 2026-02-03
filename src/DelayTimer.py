# coding=utf-8
# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


from enigma import eTimer


timer_instances = []


class DelayTimer():

    def __init__(self, delay, function, *args):
        if delay:
            timer_instances.append(self)
            self.timer = eTimer()
            self.function = function
            self.args = args
            self.timer.callback.append(self.fire)
            self.timer.start(delay, True)
        else:
            function(*args)

    def fire(self):
        if self in timer_instances:
            timer_instances.remove(self)
        if self.fire in self.timer.callback:
            self.timer.callback.remove(self.fire)
        self.function(*self.args)

    def stop(self):
        if self in timer_instances:
            timer_instances.remove(self)
            self.timer.stop()
            if self.fire in self.timer.callback:
                self.timer.callback.remove(self.fire)

    @staticmethod
    def stopAll():
        for timer_instance in timer_instances[:]:  # Create a copy to avoid modification during iteration
            timer_instance.stop()
