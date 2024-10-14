import time

def sleep_us(microseconds):
    # Busy wait in loop because delays are generally very short (few microseconds).
    end = time.time() + (microseconds/1000000.0)
    while time.time() < end:
        pass
