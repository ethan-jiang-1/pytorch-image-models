import os
import signal


class InterruptSignal(object):
    sig_num = None

    @classmethod
    def get_received_signal(cls):
        return cls.sig_num

    @classmethod
    def reset_kill_signal(cls):
        cls.sig_num = None
        print("reset sig_num")

    @classmethod
    def has_stop_signal_received(cls):
        if cls.sig_num is None:
            return False
        if hasattr(signal, "SIGUSER1"):
            if cls.sig_num == signal.SIGUSR1:
                return True
        else:
            if cls.sig_num == signal.SIGABRT:
                return True
        return False
            
    @classmethod
    def has_save_signal_received(cls):
        if cls.sig_num is None:
            return False
        if hasattr(signal, "SIGUSER2"):
            if cls.sig_num == signal.SIGUSR2:
                return True
        return False
            

    @classmethod
    def prompt_kill_signal(cls):
        pid = os.getpid()
        print()
        print('#m# start PID: {}, run following'.format(pid))
        print("")
        if hasattr(signal, "SIGUSER1"):
            print("To Stop Training and exit:")
            print("  kill -n {} {}".format(signal.SIGUSR1, pid)) 
        else:
            print("To Stop Training and exit:")
            print("  kill -n {} {}".format(signal.SIGABRT, pid)) 
        print()
        if hasattr(signal, "SIGUSER2"):
            print("To Save Model and exit:")
            print("  kill -n {} {}".format(signal.SIGUSR2, pid))
        print() 


def receive_signal_user(signum, stack):
    InterruptSignal.sig_num = signum
    print()
    print('#r# Received Interrupt Signal: {} '.format(signum))
    print()


if hasattr(signal, "SIGUSER1"):
    signal.signal(signal.SIGUSR1, receive_signal_user)
    signal.signal(signal.SIGUSR2, receive_signal_user)
else:
    signal.signal(signal.SIGABRT, receive_signal_user)
