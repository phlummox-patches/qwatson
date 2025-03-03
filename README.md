![QWatson - A simple Qt-GUI for the Watson time-tracker](
./qwatson/ressources/qwatson_banner.png)

[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](./LICENSE)
[![Latest release](https://img.shields.io/github/release/jnsebgosselin/qwatson.svg)](https://github.com/jnsebgosselin/qwatson/releases)
[![Build status](https://ci.appveyor.com/api/projects/status/f6hdeg9fyp1huxab?svg=true)](https://ci.appveyor.com/project/jnsebgosselin/qwatson)
[![codecov](https://codecov.io/gh/jnsebgosselin/qwatson/branch/master/graph/badge.svg)](https://codecov.io/gh/jnsebgosselin/qwatson)

QWatson is a simple GUI entirely written in Python with [PyQt5](https://www.riverbankcomputing.com/software/pyqt/intro) for the [Watson CLI time tracker](http://tailordev.github.io/Watson/) developed by [TailorDev](https://tailordev.fr). It is inspired by the time tracker developed by [Project Hamster](https://github.com/projecthamster/) that I love and used for several years when I was working in Linux. Unfortunately, I was not able to find any open source equivalent for the Windows platform and decided to write my own when I learned about the existence of Watson.

Many thanks to [TailorDev](https://tailordev.fr) for sharing their awesome work.

![screenshot](./images/qwatson_printscreen.png)

## To Know More About Watson

https://tailordev.fr/blog/2016/02/05/a-day-tracking-my-time-with-watson/<br>
https://tailordev.fr/blog/2016/03/31/watson-community-tools/<br>
https://tailordev.fr/blog/2017/06/07/le-lab-5-crick-a-backend-for-watson-time-tracker/

## Installation

**Windows**<br>
An installer and a binary for the Windows platform are available for download [here](https://github.com/jnsebgosselin/qwatson/releases/latest) or you can run it directly from source by cloning the repository and installing the required [dependencies](./requirements.txt).

**MacOSX and Linux**

```
$ python3 -m pip install https://github.com/phlummox-patches/qwatson/archive/refs/heads/master.zip
```

Or, using `git` to fetch a full copy of the repository:

- `git clone` this repository, `cd` in, and run `pip install .`.

**Important:**<br>
In order to support the addition of log messages/comments to the activity frames, QWatson is distributed with an extended version of Watson (see Pull Request [#1](https://github.com/jnsebgosselin/qwatson/pull/1) and [#59](https://github.com/jnsebgosselin/qwatson/pull/59)). This means that until this feature is officially supported in Watson, frames edited with QWatson won't be readable nor editable with the Watson CLI (see [Issue #37](https://github.com/jnsebgosselin/qwatson/issues/37)).

For this reason, the default path for the QWatson application folder is set differently from that of Watson, so that one does not unknowingly make its whole activity database incompatible with the Watson CLI while trying out QWatson. On first startup, QWatson will ask if you want to import your settings and data from Watson.

<p align="center"><img src="./images/import_from_watson_dialog.png" alt="Import Watson settings screenshot"></p>

This will simply copy over the configuration and data files from the Watson application folder to that of QWatson. If you decide not to import your Watson's settings and data on the first startup, it is always possible to do this afterwards by copying the files manually. Depending on your system, the default path for the application folders might be:

- Windows: C:/Users/\<user\>/AppData/Roaming/
- MacOSX: ~/Library/Application Support/
- Linux: ~/.config/

## License

QWatson is released under the GPLv3 License. See the bundled LICENSE file for details.
