
 ## Polyphinc Organ (24 voice)
 Plays the MIDI events coming from PC from the DaisySeed audio out. Synthesizing MIDI note events as a saw wave.


### Physical setup
 - USB cable between DaisySeed and PC
 - Audio jack or cable wired to Daisy Seed audio out_0 (Pin 18) + AGND (Pin 20)
 - Headphones or speaker connected to afore mentioned jack or cable (line level signal)

<img src="https://user-images.githubusercontent.com/684617/408843563-d9293aa4-dca4-4c62-b279-e9ed231157bf.png"><img>


#### To use with out compiling
Just get `DAISY_SEED_USB_MIDI_FIRMWARE.bin` from `precompiled/`

Uploading can be done via the [Daisy Web Programmer](https://electro-smith.github.io/Programmer/) from a browser

You probably will need to use [Zadig](https://zadig.akeo.ie/) to select WinUSB driver for Daisy Seed device.

### Control and Using
Included is a Virtual Midi instrument made in PyGame
<img src="https://user-images.githubusercontent.com/684617/408843810-bc6c1e29-e377-4d2f-b15d-08229e8435c2.jpg"><img>

`PyGameMidiKeyboard.py` can be used to created MIDI events to stimulate the synth.

- Run on CLI `python PyGameMidiKeyboard.py` and close, you will see a list of aviable MIDI output devices
- Run `python PyGameMidiKeyboard.py --outpust-device <DEVICE_NUMBER>`  seleceting the number corrasponding to `Daisy Seed Built In`.

Or use [Neothesia](https://polymeilex.github.io/Neothesia/) to play a midi file directly to the DaisySeed

### Enviroment setup for compiling under Windows.
See [electro-smith/DaisyWiki](https://github.com/electro-smith/DaisyWiki/wiki/1.-Setting-Up-Your-Development-Environment) or [How to Set Up Your C++ Development Environment (Daisy Tutorial) - Youtube](https://www.youtube.com/watch?v=AbvaTdAyJWk)

Roughly the required steps:
 - install [Daisy Toolchain Installer for Windows.](https://daisy.nyc3.cdn.digitaloceanspaces.com/installers/DaisyToolchain-1.1.0-win64.exe) - (Choose an install path without white space)
 - install [Git for Windows](https://gitforwindows.org/)
 - Open `gitbash` , edit and run the following to add the build tools to Bash's enviroment $PATH var. Remebering to provide your own value for DAISY_TOOLCHAIN_DIR
 ```
export DAISY_TOOLCHAIN_DIR="/c/...../DaisyToolchain"
export PATH="%DAISY_TOOLCHAIN_DIR%/bin:$PATH"
```
- `git clone --recurse-submodules` the `https://github.com/electro-smith/DaisyExamples` and run `rebuild_all.sh`
- modify the `Makefile` in this folder so that these paths point to the
```
LIBDAISY_DIR = ../DaisyExamples/libDaisy/
DAISYSP_DIR = ../DaisyExamples/DaisySP/
```
- run `make` to start compiling

- Firmware bin is `build/DAISY_SEED_USB_MIDI_FIRMWARE.bin`, can be uploaded with the
