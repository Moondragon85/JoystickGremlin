# -*- coding: utf-8; -*-

# Copyright (C) 2015 - 2017 Lionel Ott
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import time

from . import common, control_action, error, fsm, input_devices, joystick_handling, macro, tts


tts_instance = tts.TextToSpeech()



def axis_to_axis(event, value, vjoy_device_id, vjoy_input_id):
    vjoy = joystick_handling.VJoyProxy()
    vjoy[vjoy_device_id].axis(vjoy_input_id).value = value.current


def button_to_button(event, value, vjoy_device_id, vjoy_input_id):
    if event.is_pressed:
        input_devices.AutomaticButtonRelease().register(
            (vjoy_device_id, vjoy_input_id), event
        )

    vjoy = joystick_handling.VJoyProxy()
    vjoy[vjoy_device_id].button(vjoy_input_id).is_pressed = value.current


def hat_to_hat(event, value, vjoy_device_id, vjoy_input_id):
    vjoy = joystick_handling.VJoyProxy()
    vjoy[vjoy_device_id].hat(vjoy_input_id).direction = value.current


def pause(event, value):
    control_action.pause()


def resume(event, value,):
    control_action.resume()


def toggle_pause_resume(event, value):
    control_action.toggle_pause_resume()


def text_to_speech(event, value, text):
    tts_instance.speak(tts.text_substitution(text))


def switch_mode(event, value, mode):
    control_action.switch_mode(mode)


def switch_to_previous_mode(event, value):
    control_action.switch_to_previous_mode()


def cycle_modes(event, value, mode_list):
    control_action.cycle_modes(mode_list)


def run_macro(event, value, macro_fn):
    macro.MacroManager().add_macro(macro_fn, event)


def response_curve(event, value, curve_fn, deadzone_fn):
    value.current = curve_fn(deadzone_fn(value.current))


def split_axis(event, value, split_fn):
    split_fn(value.current)


def map_hat(vjoy_device_id, vjoy_input_id, data):
    vjoy = joystick_handling.VJoyProxy()
    vjoy[vjoy_device_id].hat(vjoy_input_id).direction = data


def map_key(vjoy_device_id, vjoy_input_id, data):
    vjoy = joystick_handling.VJoyProxy()
    vjoy[vjoy_device_id].button(vjoy_input_id).is_pressed = data


def press_button(vjoy_device, vjoy_input):
    vjoy = joystick_handling.VJoyProxy()
    vjoy[vjoy_device].button(vjoy_input).is_pressed = True


def release_button(vjoy_device, vjoy_input):
    vjoy = joystick_handling.VJoyProxy()
    vjoy[vjoy_device].button(vjoy_input).is_pressed = False


# FIXME: make this somehow use the actual macro default
def tap_button(vjoy_device, vjoy_input, delay=0.1):
    vjoy = joystick_handling.VJoyProxy()
    vjoy[vjoy_device].button(vjoy_input).is_pressed = True
    time.sleep(delay)
    vjoy[vjoy_device].button(vjoy_input).is_pressed = False


def run_on_press(function, is_pressed):
    if is_pressed:
        return function(is_pressed)


def run_on_release(function, is_pressed):
    if not is_pressed:
        return function(is_pressed)


class Value:

    def __init__(self, raw):
        self._raw = raw
        self._current = raw

    @property
    def raw(self):
        return self._raw

    @property
    def current(self):
        return self._current

    @current.setter
    def current(self, current):
        self._current = current


class Factory:

    @staticmethod
    def axis_to_axis(vjoy_device_id, vjoy_input_id):
        return lambda event, value: axis_to_axis(
            event,
            value,
            vjoy_device_id,
            vjoy_input_id,
        )

    @staticmethod
    def button_to_button(vjoy_device_id, vjoy_input_id):
        return lambda event, value: button_to_button(
            event,
            value,
            vjoy_device_id,
            vjoy_input_id,
        )

    @staticmethod
    def hat_to_hat(vjoy_device_id, vjoy_input_id):
        return lambda event, value: hat_to_hat(
            event,
            value,
            vjoy_device_id,
            vjoy_input_id,
        )

    @staticmethod
    def remap_input(from_type, to_type, vjoy_device_id, vjoy_input_id):
        remap_lookup = {
            (common.InputType.JoystickAxis,
             common.InputType.JoystickAxis): Factory.axis_to_axis,
            (common.InputType.JoystickButton,
             common.InputType.JoystickButton): Factory.button_to_button,
            (common.InputType.JoystickHat,
             common.InputType.JoystickHat): Factory.hat_to_hat,
        }

        remap_fn = remap_lookup.get((from_type, to_type), None)

        if remap_fn is not None:
            remap_fn(vjoy_device_id, vjoy_input_id)

    # @staticmethod
    # def map_hat(vjoy_device_id, vjoy_button_id):
    #     return lambda direction: map_hat(
    #         vjoy_device_id,
    #         vjoy_button_id,
    #         direction
    #     )
    #
    # @staticmethod
    # def tap_button(vjoy_device_id, vjoy_button_id):
    #     return lambda is_pressed: run_on_press(
    #         lambda: tap_button(vjoy_device_id, vjoy_button_id),
    #         is_pressed
    #     )
    #
    # @staticmethod
    # def tap_key(key):
    #     return lambda is_pressed: run_on_press(
    #         lambda: tap_key(key),
    #         is_pressed
    #     )

    @staticmethod
    def split_axis(split_fn):
        return lambda event, value: split_axis(
            event,
            value,
            split_fn
        )

    @staticmethod
    def response_curve(curve_fn, deadzone_fn):
        return lambda event, value: response_curve(
            event,
            value,
            curve_fn,
            deadzone_fn
        )

    @staticmethod
    def run_macro(macro_fn):
        return lambda event, value: run_macro(
            event,
            value,
            macro_fn
        )

    @staticmethod
    def switch_mode(mode):
        return lambda event, value: switch_mode(
            event,
            value,
            mode
        )

    @staticmethod
    def previous_mode():
        return lambda event, value: switch_to_previous_mode(
            event,
            value
        )

    @staticmethod
    def cycle_modes(mode_list):
        return lambda event, value: cycle_modes(
            event,
            value,
            mode_list
        )

    @staticmethod
    def pause():
        return lambda event, value: pause(
            event,
            value
        )

    @staticmethod
    def resume():
        return lambda event, value: resume(
            event,
            value
        )

    @staticmethod
    def toggle_pause_resume():
        return lambda event, value: toggle_pause_resume(
            event,
            value
        )

    @staticmethod
    def text_to_speech(text):
        return lambda event, value: text_to_speech(
            event,
            value,
            text
        )


class VirtualButton:

    """Implements a button like interface."""

    def __init__(self):
        """Creates a new instance."""
        self.callback = None
        self._fsm = self._initialize_fsm()

    def _initialize_fsm(self):
        """Initializes the state of the button FSM."""
        states = ["up", "down"]
        actions = ["press", "release"]
        transitions = {
            ("up", "press"): fsm.Transition(self._press, "down"),
            ("up", "release"): fsm.Transition(self._noop, "up"),
            ("down", "release"): fsm.Transition(self._release, "up"),
            ("down", "press"): fsm.Transition(self._noop, "down")
        }
        return fsm.FiniteStateMachine("up", states, actions, transitions)

    def _press(self):
        """Executes the "press" action."""
        self.callback(True)

    def _release(self):
        """Executes the "release" action."""
        self.callback(False)

    def _noop(self):
        """Performs no action."""
        pass

    @property
    def is_pressed(self):
        """Returns whether or not the virtual button is pressed.

        :return True if the button is pressed, False otherwise
        """
        return self._fsm.current_state == "down"


class AxisButton(VirtualButton):

    """Virtual button based around an axis."""

    def __init__(self, lower_limit, upper_limit):
        """Creates a new instance.

        :param lower_limit lower axis value where the button range starts
        :param upper_limit upper axis value where the button range stops
        """
        super().__init__()
        self._lower_limit = min(lower_limit, upper_limit)
        self._upper_limit = max(lower_limit, upper_limit)

    def process(self, value, callback):
        """Processes events for the virtual axis button.

        :param value axis position
        :param callback function to call with button events
        """
        self.callback = callback
        if self._lower_limit <= value <= self._upper_limit:
            self._fsm.perform("press")
        else:
            self._fsm.perform("release")


class HatButton(VirtualButton):

    """Virtual button based around a hat."""

    def __init__(self, directions):
        """Creates a new instance.

        :param directions hat directions used with this button
        """
        super().__init__()
        self._directions = directions

    def process(self, value, callback):
        """Process events for the virtual hat button.

        :param value hat direction
        :param callback function to call with button events
        """
        self.callback = callback
        if value in self._directions:
            self._fsm.perform("press")
        else:
            self._fsm.perform("release")


class AbstractActionContainer:

    def __init__(self, actions):
        self.actions = actions

    def _is_button_event(self, event):
        return event.event_type in [
            common.InputType.JoystickButton,
            common.InputType.Keyboard
        ]

    def __call__(self, event, value):
        raise error.GremlinError("Missing execute implementation")


class Basic(AbstractActionContainer):

    def __init__(self, actions):
        if not isinstance(actions, list):
            actions = [actions]
        super().__init__(actions)
        assert len(self.actions) == 1

    def __call__(self, event, value):
        self.actions[0](event, value)


class Tempo(AbstractActionContainer):

    def __init__(self, actions, duration):
        super().__init__(actions)
        self.duration = duration
        self.start_time = 0

    def __call__(self, event, value):
        # TODO: handle non button inputs
        if self._is_button_event(event):
            if value.current:
                self.start_time = time.time()
            else:
                if (self.start_time + self.duration) > time.time():
                    self.actions[0](event, value)
                else:
                    self.actions[1](event, value)


class Chain(AbstractActionContainer):

    def __init__(self, actions, timeout=0.0):
        super().__init__(actions)
        self.index = 0
        self.timeout = timeout
        self.last_execution = 0.0

    def __call__(self, event, value):
        # FIXME: reset via timeout not yet implemented
        if self.timeout > 0.0:
            if self.last_execution + self.timeout < time.time():
                self.index = 0
                self.last_execution = time.time()

        # TODO: handle non button inputs
        self.actions[self.index](event, value)
        if self._is_button_event(event) and not event.is_pressed:
                self.index = (self.index + 1) % len(self.actions)


class SmartToggle(AbstractActionContainer):

    def __init__(self, actions, duration=0.25):
        if not isinstance(actions, list):
            actions = [actions]
        super().__init__(actions)
        self.duration = duration

        self._init_time = 0
        self._is_toggled = False

    def __call__(self, value):
        # FIXME: breaks when held while toggle is active
        if value:
            self._init_time = time.time()
            if not self._is_toggled:
                self.actions[0](value)
        else:
            if time.time() < self._init_time + self.duration:
                # Toggle action
                if self._is_toggled:
                    self.actions[0](value)
                self._is_toggled = not self._is_toggled
            else:
                # Tap action
                self.actions[0](value)


class DoubleTap(AbstractActionContainer):

    def __init__(self, actions, timeout=0.5):
        if not isinstance(actions, list):
            actions = [actions]
        super().__init__(actions)
        self.timeout = timeout

        self._init_time = 0
        self._triggered = False

    def __call__(self, value):
        if value:
            if time.time() > self._init_time + self.timeout:
                self._init_time = time.time()
            else:
                self.actions[0](value)
                self._triggered = True
        elif not value and self._triggered:
            self.actions[0](value)
            self._triggered = False