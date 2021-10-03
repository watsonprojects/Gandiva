<div align="center">
  <div align="center">
    <img src="data/icons/128/com.github.watsonprojects.gandiva.svg" width="128">
  </div>
  <h1 align="center">Gandiva</h1>
  <div align="center">
    <img src="screenshots/screenshot.png" width="500">
  </div>
  <div align="center">Digital Personal Companion</div>
  <div>⚠️ Gandiva is in early development and not ready yet ⚠️</div>
</div>

<br/>

## Get it on elementary OS Appcenter
TBD
<!-- [![Get it on AppCenter](https://appcenter.elementary.io/badge.svg)](https://appcenter.elementary.io/com.github.watsonprojects.gandiva) -->

## Install from source
You can install gandiva by compiling it from source, here's a list of required dependencies:
 - `gtk+-3.0>=3.18`
 - `granite>=5.3.0`
 - `glib-2.0`
 - `gobject-2.0`
 - `meson`
 - `python3`


Clone repository and change directory
```
git clone https://github.com/watsonprojects/gandiva.git
cd gandiva
```
Compile, install and start gandiva on your system

Using flatpak
```
flatpak-builder build com.github.watsonprojects.gandiva.yml --user --install --force-clean
flatpak run com.github.watsonprojects.gandiva
```

Natively
```
sudo python3 setup.py install --prefix=/usr --install-data prefix/share --install-purelib prefix/share
sudo python3 post_install.py
com.github.watsonprojects.gandiva
```

<sup>**Based on**: [Elementary Python Template](https://github.com/mirkobrombin/ElementaryPython) by Mirko Brombin</sup>
<br>
<sup>**Successor to**: [Hemera](https://github.com/SubhadeepJasu/hemera) by Subhadeep Jasu. Hemera is a shell for [Mycroft AI](https://mycroft.ai), but Gandiva has it's own AI core</sup>
<br>
<sup>**License**: GNU GPLv3</sup>
<br>
<sup>© Copyright 2021-2022 Subhadeep Jasu</sup>
