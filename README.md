<div align="center">

<img src="data/images/icons/128/com.github.watsonprojects.gandiva.svg">

# Gandiva

<img src="screenshots/screenshot.png" width="500">

## Virtual AI Companion

Gandiva is the codename for an opensource virtual assistant program for Linux based operating systems. It's a voice activated accessibility tool, which is designed to simply general computing operations. It's built using python and Gtk.

https://youtu.be/H2z6n-_uqG0

[![Watch the video](https://img.youtube.com/vi/H2z6n-_uqG0/maxresdefault.jpg)](https://youtu.be/H2z6n-_uqG0)

</div>

<br>

### Main Features:
- Easy and fast file system search
- Easy and fast app search and launch apps and actions from within the app
- Talk to the program directly using voice
- Summon the program by calling "Hey Gandiva!"
- Ask questions about your computer (only Gnome and Pantheon desktops supported) [Not yet available]
- Ask trivia questions
- Control your PC using voice (only Gnome and Pantheon desktops supported) [Not yet available]
- Have basic conversation with the program [Partially available]
- Communicate with other apps via DBUS [Not yet available]
- A mandatory weather skill

<br>

### Download from AUR, Flathub and elementary OS AppCenter:

Not yet available.

--------------------------------------------------------------------------------

### Getting started:
**1) INSTALL FROM SOURCE**

You can install Gandiva from source by compiling from source. For that you will need the following:

PROGRAMMING LANGUAGES:
- `python3`
- `c`

PACKAGE UTILITIES:
- `pip3`
- `wheel`

BUILD SYSTEM:
- `meson`
- `cmake` (Required by meson)

PYTHON DEPENDENCIES:
- `pygobject`
- `numpy`
- `nltk`
- `vosk`
- `pyalsaaudio`
- `pillow`
- `py-espeak-ng`
- `geocoder`

C DEPENDENCIES:
- `python3` (C library for python 3)
- `gtk4`
- `glib-2.0`
- `libadwaita`
- `alsa`
- `pcaudiolib`
- `espeak-ng`

Once you have these, you can build it using the following commands:
```
meson _build --prefix=/usr
sudo ninja -C _build install
com.github.watsonprojects.gandiva
```

Alternatively, you can build it using <i>Flatpak</i>. For that you will need the following:

- `flatpak`
- `flatpak-builder`

Download the [elementary OS Flatpak Repo](https://flatpak.elementary.io)
and add it using

```sudo flatpak remote-add repo.flatpakrepo --if-not-exists https://flatpak.elementary.io/repo.flatpakrepo```

[Where `repo.flatpakrepo` is the file you downloaded]

FLATPAK RUNTIME AND SDK:
- `io.elementary.Platform >= 7`
- `io.elementary.Sdk >= 7`

Once you have these, you can install using the following commands:
```
flatpak-builder build  com.github.watsonprojects.gandiva.yml --user --install --force-clean
flatpak run com.github.watsonprojects.gandiva
```

**2) LAUNCHING THE APP**

Once installed you can find the app in your applications menu.
Start the app from there. On first start, you will be greeted with an initial setup screen. Set the permissions you need and you are set.

Once the app is started, it can run in background. You can always summon it using the hot word 'Hey Gandiva!'. It can take voice input and also text input using the chatbox. If Voice activation is enabled then closing the app merely puts it to sleep and it's continuously listening for hot word. Saying the hot word will bring it back up.

**3) ASKING QUESTIONS**

You can type any question in the chatbox to the right or click the mic button and speak your question. The app will answer your question or do
something that you have asked it to do. If you are not sure what to ask, there are question suggestions displayed right above the chat textbox.
You can click them to insert the suggestions in chat and send them right away.

The answer to your questions come from specific skills. Different skills handle your question in different manners. They may or may not reply using specialized speech bubbles, often containing additional information about the result or even interactable elements.

You might also notice that when you start typing the usual suggestions are replaced with files and apps on your computer. These will be discussed below.

**4) FILE SEARCH**

You can type file or folder names in the chat textbox and it will show some suggestions based on best matches. You can click on them to directly open the file or folder. You can also ask Gandiva to search for files or folders by name and the app will present you a speech bubble with all the files that match. You can also tell Gandiva to open specific libraries which are special folders for specific kind of files. For example, you ask it to open the music library and it will open the main music folder in your home folder. These libraries are opened based on XDG special user folder specification.

For file search to work in the first place the files must need to be indexed. Due to time considerations the app doesn't automatically index files yet. To index files, type in `system run index`. The process may take a long time depending on your harddrive speed and number of files. It only indexes files in the home directory (based on XDG_HOME specification)

**5) APP SEARCH** (Doesn't work in Flatpak yet)

You can similarly type in an app's name or the type of app you are looking for and Gandiva will show you suggestions based on that. You can click the suggestions to directly launch the app. You can also ask Gandiva to search apps by name, keyword or by app category. It will show you a list of apps and their supported actions, which you can directly trigger from within the app. You can also tell the app to open an app directly upon which it will open the app which best matches the name you have given.

**6) SKILLS**

For the app to work, it needs skill plugins which are loaded dynamically from the user data folder at launch. To reload and update skills manually, type in `system run relearn`.

Skills and the ones that come out of box are going to be further discussed in details below.


<br>
<sup>**Successor to**: [Hemera](https://github.com/SubhadeepJasu/hemera) by Subhadeep Jasu. Hemera is a shell for [Mycroft AI](https://mycroft.ai), but Gandiva has it's own AI core</sup>
<br>
<sup>Special thanks to Hannes Schulze for designing and programming Hemera, some of which has been ported to Gandiva now.</sup>
<br>
<sup>**License**: GNU GPLv3</sup>
<br>
<sup>© Copyright 2021-2022 Subhadeep Jasu</sup>
