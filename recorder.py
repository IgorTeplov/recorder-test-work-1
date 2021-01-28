from pydub.playback import play
import alsaaudio
import threading
import argparse
import pyaudio
import pydub
import wave
import sys
import os
import re


class Recorder(object):
    __STOP_RECORDING = True
    __END_RECORDING = False

    p = pyaudio.PyAudio()
    frame_counter = 0
    ready_chunks = 0

    help_ = '''Enter:
    s: to stop recording
    r: to resume recording
    e: to exit'''
    min_time = 'Minimum recording length {} seconds. Please wait ...'

    def __init__(self, args, rate: int=44100, channels: int=2,
                 sample_format: int=pyaudio.paInt16,
                 chunk: int=1024, min_recording_time: int=5,
                 max_recording_time: int=60):

        self._path = args.path
        self._rate = rate
        self._sample_format = sample_format
        self._channels = channels
        self._chunk = chunk
        self._min_recording_time = min_recording_time
        self._max_recording_time = max_recording_time
        self.stream = self.p.open(
            format=self._sample_format,
            channels=self._channels,
            rate=self._rate,
            frames_per_buffer=self._chunk,
            input=True,
            output=True
        )

    @property
    def min_recording_time(self):
        return int(self._rate / self._chunk * self._min_recording_time)

    @property
    def max_recording_time(self):
        return int(self._rate / self._chunk * self._max_recording_time)

    def _main_loop(self):
        # основной цикл
        # открывает файл на запись
        # получает данные с микрофона
        # и отправляет их на запись и воспроизведение

        # если мы останавливает его раньше минимального
        # времени записи то он записывает еще 5 секунд
        # и выключаеться
        with wave.open(self._path, 'wb') as wf:
            wf.setnchannels(self._channels)
            wf.setsampwidth(self.p.get_sample_size(self._sample_format))
            wf.setframerate(self._rate)

            while self.frame_counter <= self.max_recording_time:
                if self.__END_RECORDING:
                    if self.frame_counter > self.min_recording_time:
                        break
                    else:
                        if self.stream.get_write_available() > self._chunk:
                            os.system('clear')
                            time = self._min_recording_time
                            print(self.min_time.format(time),
                                  end='', flush=True)
                            print('\r', end='')
                        if self.__STOP_RECORDING:
                            self.__STOP_RECORDING = False

                data = self.stream.read(self._chunk)
                if not self.__STOP_RECORDING:
                    self.ready_chunks = self.stream.get_write_available()
                    self.frame_counter += 1

                    self._create_chunk([data])

                    talker = threading.Thread(target=self._play_chunk,
                                              args=(wf, ), daemon=True)
                    talker.start()
                    talker.join()

        self._exit()

    def _controller_loop(self):
        # цикл ввода команд
        # отключается когда мы заканчиваем запись

        # поддерживает три команды

        # остановка записи
        # возобновление записи
        # завершение записи
        while self.main_loop.is_alive():
            cmd = input()
            if cmd == 's':
                self.__STOP_RECORDING = True
                self.ready_chunks = 0
            elif cmd == 'r':
                self.__STOP_RECORDING = False
            elif cmd == 'e':
                self.__END_RECORDING = True
                if not self.frame_counter > self.min_recording_time:
                    self._min_recording_time = self._get_seconds() + 5

    def _view_loop(self):
        # цикл вывода информации о записи
        # отключается когда мы вводим команду заканчить запись
        massage_rec = 'Recording        ... Recording time: {} seconds.'
        massage_pas = 'Recording paused ... Recording time: {} seconds.'
        while self.main_loop.is_alive():
            if self.__END_RECORDING:
                break
            if self.ready_chunks > self._chunk:
                os.system('clear')
                print(self.help_)
            if not self.__STOP_RECORDING:
                print(massage_rec.format(self._get_seconds()),
                      end='', flush=True)
                print('\r', end='')
            else:
                print(massage_pas.format(self._get_seconds()),
                      end='', flush=True)
                print('\r', end='')

    def _play_chunk(self, wave_file):
        # записывает фрейм данных из временного файла
        # и воспроизводит его
        pdf = pydub.AudioSegment.from_wav('chunk.wav') + 12
        data = pdf.__dict__['_data']
        wave_file.writeframes(data)
        self.stream.write(data)

    def _create_chunk(self, frames: list):
        # создает временный файл и записует в него фрейм данных
        with wave.open('chunk.wav', 'wb') as wf:
            wf.setnchannels(self._channels)
            wf.setsampwidth(self.p.get_sample_size(self._sample_format))
            wf.setframerate(self._rate)
            wf.writeframes(b"".join(frames))

    def _get_seconds(self):
        # возвращает время записи
        if self.frame_counter != 0:
            return round(self.frame_counter/int(self._rate / self._chunk))
        return 0

    def _exit(self):
        # закрытие потока данных и удаление временного файла
        if os.path.isfile('chunk.wav'):
            os.remove('chunk.wav')
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

        massage = 'Finished recording! Recording time {} seconds.'
        print('\n', end='')
        print(massage.format(self._get_seconds()))

    def run(self):
        # запуск трёх потоков
        # главный поток
        # один на ввод информации
        # один на вывод информации

        os.system('clear')
        print(self.help_)
        mix = alsaaudio.Mixer()
        vol = mix.getvolume()[0]
        vol = vol*2 if vol*2 < 100 else 100
        mix.setvolume(vol)

        self.main_loop = threading.Thread(target=self._main_loop)
        self.main_loop.start()

        controller_loop = threading.Thread(target=self._controller_loop,
                                           daemon=True)
        controller_loop.start()
        view_loop = threading.Thread(target=self._view_loop)
        view_loop.start()


def file_path_validator(path):

    abspath_valid = re.match(r"^/(.+/)*(.+)/.(.+)$", path)
    if abspath_valid is not None:
        if abspath_valid is not None:
            if not os.path.isdir(os.path.dirname(path)):
                try:
                    os.makedirs(os.path.dirname(path))
                except PermissionError:
                    path_f = os.path.dirname(path)
                    print(f"You cannot create folder. ({path_f})")
                    sys.exit(-1)
            else:
                if os.path.isfile(path):
                    print(f'Do you want to overwrite this file? ({path})')
                    if input('y/n: ') == 'n':
                        sys.exit(0)
                else:
                    try:
                        with open(path, 'x') as file:
                            pass
                    except PermissionError:
                        print(f"You cannot create file. ({path})")
                        sys.exit(-1)
    else:
        raise argparse.ArgumentTypeError(f"{path} file path is invalid.")
    return path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('path', type=file_path_validator,
                        help='Recording file path.')
    args = parser.parse_args()

    app = Recorder(args)
    app.run()


if __name__ == '__main__' and sys.platform.startswith('linux'):
    main()
