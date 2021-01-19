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


def print_status(s):
    print(s.ljust(50), end='\r')


def print_line(s):
    print(s.ljust(50))


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
    class Signal(Enum):
        DOT = auto()
        DASH = auto()
        SHORT_PAUSE = auto()
        MEDIUM_PAUSE = auto()
        LONG_PAUSE = auto()

    current_word = ''
    current_symbol = ''
    __last_rise = 0
    __last_fall = 0

    def __init__(self, interval, max_input_deviation, max_pause_deviation, too_long_is_dash):
        self.debouncer = Debouncer(PIN_BTN, GPIO.PUD_UP)
        self.interval = interval
        self.max_input_deviation = max_input_deviation
        self.max_pause_deviation = max_pause_deviation
        self.too_long_is_dash = too_long_is_dash

    def value_in_interval(self, value, max_deviation, interval_multiplier):
        interval = self.interval * interval_multiplier
        if (interval - max_deviation) <= value <= (interval + max_deviation):
            return True
        return False

    def input_in_interval(self, value, interval_multiplier=1):
        return self.value_in_interval(value, self.max_input_deviation, interval_multiplier)

    def pause_in_interval(self, value, interval_multiplier=1):
        return self.value_in_interval(value, self.max_pause_deviation, interval_multiplier)

    def read_one_signal(self):
        signal = None
        time_now = time.monotonic_ns()

        if self.debouncer.rise():
            self.__last_rise = time_now
            elapsed_ms = (self.__last_rise - self.__last_fall) // 1000000

            if self.pause_in_interval(elapsed_ms, 3):
                signal = self.Signal.MEDIUM_PAUSE

        elif self.debouncer.fall():
            self.__last_fall = time_now
            elapsed_ms = (self.__last_fall - self.__last_rise) // 1000000

            if self.input_in_interval(elapsed_ms):
                signal = self.Signal.DOT
            elif self.input_in_interval(elapsed_ms, 3):
                signal = self.Signal.DASH
            elif self.too_long_is_dash and elapsed_ms > (self.interval * 3):
                signal = self.Signal.DASH
            else:
                print_line('The input was neither a dot or dash')

        elif self.__last_fall > self.__last_rise:
            elapsed_ms = (time_now - self.__last_fall) // 1000000
            print_status('Pause duration: ' + str(elapsed_ms))

            if elapsed_ms >= (self.interval * 7):
                signal = self.Signal.LONG_PAUSE
                self.__last_rise = 0
                self.__last_fall = 0
        elif self.__last_rise > self.__last_fall:
            elapsed_ms = (time_now - self.__last_rise) // 1000000
            print_status('Input duration: ' + str(elapsed_ms))

        return signal

    def process_signal(self, signal):
        if signal in [self.Signal.DOT, self.Signal.DASH]:
            self.update_current_symbol(signal)
        elif signal is self.Signal.MEDIUM_PAUSE:
            self.handle_symbol_end()
        elif signal is self.Signal.LONG_PAUSE:
            self.handle_word_end()

    def update_current_symbol(self, signal):
        if signal is self.Signal.DOT:
            self.current_symbol += '.'
        else:
            self.current_symbol += '-'

    def handle_symbol_end(self):
        self.update_current_word(MORSE_CODE.get(self.current_symbol, '_'))
        self.current_symbol = ''

    def update_current_word(self, symbol):
        self.current_word += symbol

    def handle_word_end(self):
        self.handle_symbol_end()
        print_line(self.current_word)
        self.current_word = ''

    def run_decoding_loop(self):
        while True:
            self.debouncer.update()
            signal = self.read_one_signal()
            if signal is not None:
                self.process_signal(signal)


def main():
    GPIO.setup(PIN_BLUE_LED, GPIO.OUT, GPIO.LOW)
    GPIO.setup(PIN_RED_LED_0, GPIO.OUT, GPIO.LOW)
    GPIO.setup(PIN_RED_LED_1, GPIO.OUT, GPIO.LOW)
    GPIO.setup(PIN_RED_LED_2, GPIO.OUT, GPIO.LOW)
    GPIO.setup(PIN_BTN, GPIO.IN, GPIO.PUD_UP)

    interval = int(input('Choose a time interval for T (in ms): '))
    input_deviation = int(
        input('Choose a max deviation for each input (in ms): '))

    pause_deviation = input(
        'Choose a max deviation for each pause (in ms) [Press ENTER for same as input]: ')
    if pause_deviation == "":
        pause_deviation = input_deviation
    else:
        pause_deviation = int(pause_deviation)

    too_long_is_dash = input(
        'Should an input that is too long be recognized as a dash? [Y/n]: ')
    if too_long_is_dash == '' or too_long_is_dash.lower() == 'y':
        too_long_is_dash = True
    else:
        too_long_is_dash = False

    decoder = MorseDecoder(interval, input_deviation,
                           pause_deviation, too_long_is_dash)
    decoder.run_decoding_loop()


if __name__ == '__main__':
    main()
