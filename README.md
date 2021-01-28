# Recorder (only linux)

## RU
### Для запуска понадобиться:

- python3
- portaudio19-dev 
- python-pyaudio
- python-alsaaudio

а также запустить на установку модули из файла requirements.txt.

### Инструкция по использованию.

Запустить python3 recorder.py /путь/к/файлу.wav

- Для начала записи нажать 'r' и 'enter'.
- Для остановки записи нажать 's' и 'enter'.
- Для прекращения записи нажать 'e' и 'enter'.

1. Минимальное время записи 5 секунд.
2. Максимальное время записи 60 секунд.
3. Если прекратить запись раньше 5 секунд, программа будет работатьеще 5 секунд и только потом выключиться.
4. Если остановить программу, и через время больше 5 секунд закончитьзапись результат будет аналогичным прекращению записи раньше 5 секунд.

## EN
### To run you need:

- python3
- portaudio19-dev 
- python-pyaudio
- python-alsaaudio

and also run the modules from the requirements.txt file for installation.

### Instructions for use.

Run python3 recorder.py /path/to/file.wav

- To start recording press 'r' and 'enter'.
- To stop recording press 's' and 'enter'.
- To stop recording press 'e' and 'enter'.

1. Minimum recording time 5 seconds.
2. Maximum recording time 60 seconds.
4. If you stop recording before 5 seconds, this program will work another 5 seconds and only then turn off.
5. If you stop the program and finish recording after more than 5 seconds, the result will be the same as stopping recording before 5 seconds.
