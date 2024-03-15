import argparse
import struct
import wave

from picovoice import *
from pvrecorder import PvRecorder

accessKey = '5NRGXNhNwR3KUOUNdF882hmfhd3zDLt4zb00AWvPlI5N30HEhDbYoQ=='
keywordPath = 'wakeword.ppn'
contextPath = 'context.rhn'
wakeSensitivity = 0.5
contextSensitivity = 0.5
endPointDuration = 1
audioDeviceIndex = 0
outputPath = ''


def main():
    require_endpoint = True

    for i, device in enumerate(PvRecorder.get_available_devices()):
        print('Device %d: %s' % (i, device))

    def wake_word_callback():
        print('New Calculation:')

    def inference_callback(inference):
        if inference.is_understood:
            answer = int(inference.slots['n1']) + int(inference.slots['n2'])
            print(inference.slots['n1'] + ' + ' + inference.slots['n2'] + ' = ' + str(answer))
        else:
            print("Didn't understand the command.\n")

    try:
        picovoice = Picovoice(
            access_key=accessKey,
            keyword_path=keywordPath,
            wake_word_callback=wake_word_callback,
            context_path=contextPath,
            inference_callback=inference_callback,
            porcupine_sensitivity=wakeSensitivity,
            rhino_sensitivity=contextSensitivity,
            endpoint_duration_sec=endPointDuration,
            require_endpoint=require_endpoint)
    except PicovoiceInvalidArgumentError as e:
        print("One or more arguments provided to Picovoice is invalid: ", args)
        print(e)
        raise e
    except PicovoiceActivationError as e:
        print("AccessKey activation error")
        raise e
    except PicovoiceActivationLimitError as e:
        print("AccessKey '%s' has reached it's temporary device limit" % args.access_key)
        raise e
    except PicovoiceActivationRefusedError as e:
        print("AccessKey '%s' refused" % args.access_key)
        raise e
    except PicovoiceActivationThrottledError as e:
        print("AccessKey '%s' has been throttled" % args.access_key)
        raise e
    except PicovoiceError as e:
        print("Failed to initialize Picovoice")
        raise e

    print('Picovoice version: %s' % picovoice.version)

    recorder = PvRecorder(
        frame_length=picovoice.frame_length,
        device_index=audioDeviceIndex,
    )
    recorder.start()

    print('Listening ... (Press Ctrl+C to exit)\n')

    wav_file = None
    if outputPath != '':
        wav_file = wave.open(outputPath, 'wb')
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(picovoice.sample_rate)

    try:
        while True:
            pcm = recorder.read()

            if wav_file is not None:
                wav_file.writeframes(struct.pack("h" * len(pcm), *pcm))

            picovoice.process(pcm)

    except KeyboardInterrupt:
        print('Stopping ...')
    finally:
        recorder.delete()
        picovoice.delete()
        if wav_file is not None:
            wav_file.close()


if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
