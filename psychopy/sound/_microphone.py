#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Audio recording using a microphone.
"""

# Part of the PsychoPy library
# Copyright (C) 2002-2018 Jonathan Peirce (C) 2019-2021 Open Science Tools Ltd.
# Distributed under the terms of the GNU General Public License (GPL).

__all__ = ['Microphone']

import sys

try:
    import psychtoolbox as ptb
    import psychtoolbox.audio as audio
except (ImportError, ModuleNotFoundError):
    raise ImportError("psychtoolbox audio failed to import")

from psychopy.constants import NOT_STARTED, STARTED
from ._audioclip import *
from ._audiodevice import *
from ._exceptions import AudioStreamError


class Microphone(object):
    """Class for recording audio from a microphone.

    Parameters
    ----------
    sampleRateHz : int
        Sampling rate for audio recording in Hertz (Hz). By default, 48kHz
        (``sampleRateHz=480000``) is used which is adequate for most consumer
        grade microphones (headsets and built-in). Sampling rates should be at
        least greater than 20kHz to minimize distortion perceptible to humans
        due to aliasing.
    channels : int
        Number of channels to use.

    Examples
    --------
    Capture 10 seconds of audio from the primary microphone::

        import psychopy.core as core
        import psychopy.sound.Microphone as Microphone

        mic = Microphone()  # open the microphone
        mic.start()  # start recording
        core.wait(10.0)  # wait 10 seconds
        audioClip = mic.getAudioClip()  # get the audio data
        mic.stop()  # stop recording

        print(audioClip.duration)  # should be ~10 seconds
        audioClip.save('test.wav')  # save the recorded audio as a 'wav' file

    """
    def __init__(self,
                 device=None,
                 sampleRateHz=SAMPLE_RATE_48kHz,
                 channels=2,
                 mode=2,
                 recBufferSecs=10.0):

        # get information about the selected device
        self._device = device

        self._sampleRateHz = sampleRateHz
        # internal recording buffer size in seconds
        assert isinstance(recBufferSecs, (float, int))
        self._recBufferSecs = float(recBufferSecs)

        # PTB specific stuff (for now, might move to base class)
        self._mode = int(mode)
        self._channels = int(channels)

        # this can only be set after initialization
        self._stopTime = None   # optional, stop time to end recording

        # handle for the recording stream
        self._recording = self._createStream()

        # pre-allocate recording buffer
        self._recording.get_audio_data(self._recBufferSecs)

        # status flag
        self._statusFlag = NOT_STARTED

    @staticmethod
    def getDevices():
        """Get a `dict` of audio capture device (i.e. microphones) descriptors.
        On Windows, only WASAPI devices are used.

        Returns
        -------
        list
            List of `AudioDevice` descriptors for suitable capture devices.

        """
        # query PTB for devices
        allDevs = audio.get_devices(
            device_type=(
                13 if sys.platform == 'win32' else None))  # WASAPI only

        # make sure we have an array
        allDevs = [allDevs] if isinstance(allDevs, dict) else allDevs

        # create list of descriptors only for capture devices
        inputDevices = [desc for desc in [
            AudioDevice.createFromPTBDeviceDesc(dev) for dev in allDevs]
                     if desc.isCapture]

        return inputDevices

    def _createStream(self):
        """Create a new stream handle.
        """
        return audio.Stream(
            mode=self._mode,
            freq=self._sampleRateHz,
            channels=self._channels)

    @property
    def recordingBufferSecs(self):
        """Size of the internal audio storage buffer in seconds (`float`).
        Cannot be set while recording.

        """
        return self._recBufferSecs

    @property
    def stopTime(self):
        """Duration of the audio recording (`float`). Cannot be set while a
        recording is in progress.

        """
        return self._stopTime

    @stopTime.setter
    def stopTime(self, value):
        assert isinstance(value, (float, int))
        self._stopTime = float(value)

    def start(self):
        """Start an audio recording.

        Calling this method will open a stream and begin capturing samples from
        the microphone.

        """
        # check if the stream has been
        if self._statusFlag == STARTED:  # raise warning, error, or ignore?
            pass

        assert self._recording is not None  # must have a handle
        self._recording.start(repetitions=0, stop_time=self._stopTime)
        self._statusFlag = STARTED  # recording has begun

    def stop(self):
        """Stop recording audio.

        Call this method to end an audio recording if in progress. This will
        close the audio stream.

        """
        self._recording.stop()
        self._statusFlag = NOT_STARTED

    def close(self):
        """Close the stream."""
        self._recording.close()

    def getAudioClip(self, clipName=None):
        """Get samples from a previous recording."""
        if self._statusFlag == NOT_STARTED:
            raise AudioStreamError(
                "Cannot get stream data while stream is closed.")

        # REM - write these other values to the clip header
        audioData, _, _, _ = self._recording.get_audio_data()

        return AudioClip(
            samples=audioData,
            sampleRateHz=self._sampleRateHz)


if __name__ == "__main__":
    pass
