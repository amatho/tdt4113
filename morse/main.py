from GPIOSimulator_v1 import GPIOSimulator, PIN_BLUE_LED, PIN_BTN, PIN_RED_LED_0, PIN_RED_LED_1, PIN_RED_LED_2
import time
import keyboard
from enum import Enum, auto

GPIO = GPIOSimulator()

MORSE_CODE = {'.-': 'a', '-...': 'b', '-.-.': 'c', '-..': 'd', '.': 'e', '..-.': 'f', '--.': 'g',
              '....': 'h', '..': 'i', '.---': 'j', '-.-': 'k', '.-..': 'l', '--': 'm', '-.': 'n',
              '---': 'o', '.--.': 'p', '--.-': 'q', '.-.': 'r', '...': 's', '-': 't', '..-': 'u',
              '...-': 'v', '.--': 'w', '-..-': 'x', '-.--': 'y', '--..': 'z', '.----': '1',
              '..---': '2', '...--': '3', '....-': '4', '.....': '5', '-....': '6', '--...': '7',
              '---..': '8', '----.': '9', '-----': '0'}


class Debouncer:
    class FallRiseState(Enum):
        UNCHANGED = auto()
        FALL = auto()
        RISE = auto()

    def __init__(self, pin, initial_stable_value, stable_time=2000000):
        self.__pin = pin
        self.__stable_time = stable_time
        self.value = initial_stable_value
        self.__last_state = initial_stable_value
        self.__fall_rise_state = self.FallRiseState.UNCHANGED
        self.__time_changed = time.monotonic_ns()

    def update(self):
        state = GPIO.input(self.__pin)
        time_now = time.monotonic_ns()
        if state is self.__last_state and time_now - self.__time_changed > self.__stable_time:
            # State is stable, update the value
            self.__last_stable_value = self.value
            self.value = state
            if self.__last_stable_value is GPIO.LOW and self.value is GPIO.HIGH:
                self.__fall_rise_state = self.FallRiseState.RISE
            elif self.__last_stable_value is GPIO.HIGH and self.value is GPIO.LOW:
                self.__fall_rise_state = self.FallRiseState.FALL
            else:
                self.__fall_rise_state = self.FallRiseState.UNCHANGED
        elif state is not self.__last_state:
            # State changed since last update
            self.__time_changed = time_now

        self.__last_state = state

    def rise(self):
        if self.__fall_rise_state == self.FallRiseState.RISE:
            # Make sure rise() only returns True once
            self.__fall_rise_state = self.FallRiseState.UNCHANGED
            return True

        return False

    def fall(self):
        if self.__fall_rise_state == self.FallRiseState.FALL:
            # Make sure fall() only returns True once
            self.__fall_rise_state = self.FallRiseState.UNCHANGED
            return True

        return False


class MorseDecoder:

    def __init__(self):
        self.debouncer = Debouncer(PIN_BTN, GPIO.PUD_UP)
        self.__max_deviance_ms = 100

    def run_decoding_loop(self):
        while True:
            self.debouncer.update()
            if self.debouncer.rise():
                print('Started pressing!')
            elif self.debouncer.fall():
                print('Stopped pressing!')


def main():
    GPIO.setup(PIN_BLUE_LED, GPIO.OUT, GPIO.LOW)
    GPIO.setup(PIN_RED_LED_0, GPIO.OUT, GPIO.LOW)
    GPIO.setup(PIN_RED_LED_1, GPIO.OUT, GPIO.LOW)
    GPIO.setup(PIN_RED_LED_2, GPIO.OUT, GPIO.LOW)
    GPIO.setup(PIN_BTN, GPIO.IN, GPIO.PUD_UP)

    decoder = MorseDecoder()
    decoder.run_decoding_loop()


if __name__ == '__main__':
    main()
