
 ## Polyphonic Organ (24 voice)
 Plays the MIDI events coming from PC from the DaisySeed audio out. Synthesizing MIDI note events as a saw wave.


### Physical setup
 - USB cable between DaisySeed and PC
 - Audio jack or cable wired to Daisy Seed audio out_0 (Pin 18) + AGND{Analog Ground} (Pin 20)
 - Headphones or speaker connected to afore mentioned jack or cable (line level signal)

![HardwareSetup](https://github.com/user-attachments/assets/8f38cbd2-f173-4d8e-b681-1b4cf840e8a0)


#### To use with out compiling
Just get `DAISY_SEED_USB_MIDI_FIRMWARE.bin` from `precompiled/`

Uploading can be done via the [Daisy Web Programmer](https://electro-smith.github.io/Programmer/) from a browser

You probably will need to use [Zadig](https://zadig.akeo.ie/) to select WinUSB driver for Daisy Seed device.

### Control and Using
Included is a Virtual Midi instrument made in PyGame

![CLI Command and PyGame GUI](https://github.com/user-attachments/assets/a638dd5f-3c8a-4fc7-b87b-ef6473b5d6ab)

`PyGameMidiKeyboard.py` can be used to created MIDI events to stimulate the synth.

- Run on CLI `python PyGameMidiKeyboard.py` and close, you will see a list of available MIDI output devices
- Run `python PyGameMidiKeyboard.py --output-device <DEVICE_NUMBER>`  selecting the number corresponding to `Daisy Seed Built In`.

Or use [Neothesia](https://polymeilex.github.io/Neothesia/) to play a midi file directly to the DaisySeed

### Enviroment setup for compiling under Windows.
See [electro-smith/DaisyWiki](https://github.com/electro-smith/DaisyWiki/wiki/1.-Setting-Up-Your-Development-Environment) or [How to Set Up Your C++ Development Environment (Daisy Tutorial) - Youtube](https://www.youtube.com/watch?v=AbvaTdAyJWk)

Roughly the required steps:
 - install [Daisy Toolchain Installer for Windows.](https://daisy.nyc3.cdn.digitaloceanspaces.com/installers/DaisyToolchain-1.1.0-win64.exe) - (Choose an install path without white space)
 - install [Git for Windows](https://gitforwindows.org/)
 - Open `gitbash` , edit and run the following to add the build tools to Bash's environment $PATH var. Remembering to provide your own value for DAISY_TOOLCHAIN_DIR
 ```
export DAISY_TOOLCHAIN_DIR="/c/...../DaisyToolchain"
export PATH="%DAISY_TOOLCHAIN_DIR%/bin:$PATH"
```
- `git clone --recurse-submodules` the `https://github.com/electro-smith/DaisyExamples` and run `rebuild_all.sh`
- modify the `Makefile` in this folder so that these paths point to the correct path where libDaisy and DaisySP have been compiled to e.g. where you cloned `DaisyExamples` repo to.
```
LIBDAISY_DIR = ../DaisyExamples/libDaisy/
DAISYSP_DIR = ../DaisyExamples/DaisySP/
```
- run `make` to start compiling

- Firmware bin is `build/DAISY_SEED_USB_MIDI_FIRMWARE.bin`, can be uploaded with the
