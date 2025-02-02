import pygame
import pygame.midi
import rtmidi
import time
import argparse
from collections import deque
from dataclasses import dataclass
from typing import List, Deque, Optional, Callable
from datetime import datetime

"""
Simple GUI for Keyboard inputs as MIDI output.
    To Select the MIDI destination:
    use argument: --output-device <DEVICE_NUMBER>

Has the layout of a standard tuned gutiar. Assumes QWERTY keyboard.
"""

@dataclass
class MidiEvent:
    note: int
    velocity: int
    timestamp: float

@dataclass
class PianoButton:
    rect: pygame.Rect
    keyboard_key:pygame.key
    color: tuple
    note: int
    is_pressed: bool = False
    label: str = ""

class MidiBuffer:
    def __init__(self, buffer_duration: float = 30.0):
        self.buffer: Deque[MidiEvent] = deque()
        self.buffer_duration = buffer_duration
        self.start_time = time.time()

    def add_event(self, event: MidiEvent):
        current_time = time.time() - self.start_time
        self.buffer.append(event)
        
        # Cleanup old events
        while (self.buffer and 
               current_time - self.buffer[0].timestamp > self.buffer_duration):
            self.buffer.popleft()


    def render(self, surface: pygame.Surface, viewport_rect: pygame.Rect, current_relative_time: float):
        """
        Render MIDI notes as rectangles on a pygame surface.
        
        Args:
            surface: Pygame surface to render on
            viewport_rect: Rectangle defining the rendering area
            current_relative_time: Current time relative to start time
        """
        # Define the time window
        time_window = 10.0  # 10 seconds window
        window_start = current_relative_time - time_window
        window_end = current_relative_time
        
        # Calculate scaling factors
        time_scale = viewport_rect.width / time_window
        note_height = 4  # Height of each note in pixels
        
        # A2(45) to A7(93)
        note_range = 48  # 93 - 45 = 48 semitones total
        note_start = 45
        note_scale = viewport_rect.height / note_range
        
        # Draw background
        pygame.draw.rect(surface, (20, 20, 20), viewport_rect)
        
        # Draw piano roll grid lines (every octave)
        for octave in range(5):  # From A2 to A7
            midi_note = note_start + (octave * 12)  # Start from A2 and go up by octaves
            y_pos = viewport_rect.bottom - ((midi_note - note_start) * note_scale)
            pygame.draw.line(surface, (40, 40, 40),
                            (viewport_rect.left, y_pos),
                            (viewport_rect.right, y_pos))
        
        # Keep track of active notes for proper rendering of note duration
        active_notes = {}  # note_number -> (start_time, note_rectangle)
        
        # Process all events in the buffer
        for event in self.buffer:
            if event.timestamp < window_start or event.timestamp > window_end:
                continue
                
            # Calculate x position based on event timestamp
            event_x = viewport_rect.left + ((event.timestamp - window_start) * time_scale)
            
            if event.velocity > 0:
                if note_start <= event.note <= 93:  # Only process notes in our range
                    # Calculate y position relative to our note range
                    note_y = viewport_rect.bottom - ((event.note - note_start) * note_scale)
                    active_notes[event.note] = (event.timestamp, pygame.Rect(
                        event_x, note_y - note_height, 2, note_height  # Start with minimal width
                    ))
                
            elif event.velocity == 0:
                if event.note in active_notes:
                    start_time, note_rect = active_notes[event.note]
                    # Calculate final width based on note duration
                    note_duration = event.timestamp - start_time
                    note_width = note_duration * time_scale
                    note_rect.width = max(1, note_width)
                    
                    # Draw the note rectangle with color based on velocity
                    velocity_color = min(255, event.velocity * 2)
                    color = (velocity_color, velocity_color, 255)
                    pygame.draw.rect(surface, color, note_rect)
                    del active_notes[event.note]
        
        # Draw any still-active notes
        for note, (start_time, note_rect) in active_notes.items():
            # Calculate width based on current time
            note_duration = current_relative_time - start_time
            note_width = note_duration * time_scale
            note_rect.width = max(1, note_width)
            
            # Draw still-active notes in a different color
            pygame.draw.rect(surface, (100, 255, 100), note_rect)
        
        # Draw playhead line at current time
        playhead_x = viewport_rect.right
        pygame.draw.line(surface, (255, 50, 50),
                        (playhead_x, viewport_rect.top),
                        (playhead_x, viewport_rect.bottom), 2)

class MidiDevice:
    def __init__(self, port_name: str = None):
        self.midiout = rtmidi.MidiOut()
        self.port_name = port_name
        self.port_index = self._find_port()
        
        if self.port_index is not None:
            self.midiout.open_port(self.port_index)
            print(f"Opened MIDI port: {port_name}")
        else:
            print("No MIDI port found matching the specified name")
            self._list_ports()
            raise ValueError("Invalid MIDI port name")

    def _find_port(self) -> Optional[int]:
        available_ports = self.midiout.get_ports()
        if self.port_name:
            for i, port in enumerate(available_ports):
                if self.port_name.lower() in port.lower():
                    return i
        return None if not available_ports else 0

    @staticmethod
    def _list_ports():
        midi_out = rtmidi.MidiOut()
        ports = midi_out.get_ports()
        print("\nAvailable MIDI ports:")
        for i, port in enumerate(ports):
            print(f"{i}: {port}")
        midi_out.delete()

    def send_message(self, message: List[int]):
        if self.midiout:
            self.midiout.send_message(message)

    def cleanup(self):
        if self.midiout:
            self.midiout.close_port()


class MidiPiano:
    "Its a guitar layout"
    NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    BUTTON_KEYS = (
        "            "
        "            "
        '1234567890-='
        "qwertyuiop[]"
        "asdfghjkl;' "
        "zxcvbnm,./  "
    )

    def __init__(self, midi_device: MidiDevice):
        pygame.init()
        pygame.midi.init()
        
        self.width = 1200
        self.height = 800
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("MIDI Piano")
        
        self.midi_device = midi_device
        self.event_handlers: List[Callable[[MidiEvent], None]] = []
        
        self.margin = 20
        self.button_width = 80
        self.button_height = 80
        self.grid_offset = 60  # Space for save button and other controls
        
        # Create button grid
        self.buttons = self.create_button_grid(start_note=40) 
        
        self.save_button = pygame.Rect(250, 320, 100, 40)

        # Initialize font
        self.font = pygame.font.Font(None, 24)
    
    def create_button_grid(self, start_note: int) -> List[PianoButton]:
        buttons = []
        rows = 6
        cols = 12
        key_index = 0
        for row in range(rows):
            for col in range(cols):
                warp = +1 if row > 1 else 0
                start_note = 40
                note_number =(
                    (128 - start_note)
                    - ((row+1) * 12 )
                    + col
                    + (row * 7)
                    + warp
                    )
                x = self.margin + col * (self.button_width + 5)
                y = self.grid_offset + row * (self.button_height + 5)
                
                # Get note name and octave
                note_name = self.NOTE_NAMES[note_number % 12]
                octave = (note_number // 12) - 1
                label = f"{note_name}{octave}"
                
                # Use different colors for white and black keys
                is_black_key = '#' in note_name
                color = (80, 80, 80) if is_black_key else (200, 200, 200)
                
                # Assign a key from BUTTON_KEYS to this button
                if key_index < len(self.BUTTON_KEYS):
                    keyboard_key = self.BUTTON_KEYS[key_index]
                    key_index = (key_index + 1)
                    if keyboard_key == ' ':
                        keyboard_key=None
                else:
                    keyboard_key=None

                button = PianoButton(
                    rect=pygame.Rect(x, y, self.button_width, self.button_height),
                    keyboard_key=keyboard_key,
                    color=color,
                    note=note_number,
                    label=label,
                )

                
                buttons.append(button)
        
        return buttons

    def add_event_handler(self, handler: Callable[[MidiEvent], None]):
        self.event_handlers.append(handler)

    def emit_midi_event(self, note: int, velocity: int):
        """Emit MIDI event to device and notify handlers"""
        if velocity > 0:
            self.midi_device.send_message([0x90, note, velocity])
        else:
            self.midi_device.send_message([0x80, note, 0])
            
        event = MidiEvent(note, velocity, time.time())
        for handler in self.event_handlers:
            handler(event)

    def run(self, midi_buffer):


        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                # if event.type == pygame.MOUSEBUTTONDOWN:
                    # if self.save_button.collidepoint(event.pos):
                    #     self.emit_midi_event(0, 0)  # Signal for save
                
                if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.KEYDOWN, pygame.KEYUP]:
                    for button in self.buttons:
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            if button.rect.collidepoint(event.pos) and not button.is_pressed:
                                button.is_pressed = True
                                self.emit_midi_event(button.note, 100)

                        # Currently, this clears all pressed notes. So to handle MOUSEBUTTONUP outside the button area.
                        # TODO Should ignore buttons depressed by Keyboard input.
                        # Otherwise needs a more comprehensive mouse interaction model.
                        elif event.type == pygame.MOUSEBUTTONUP:
                            if button.is_pressed:
                                button.is_pressed = False
                                self.emit_midi_event(button.note, 0)

                        elif event.type == pygame.KEYDOWN:
                            if button.keyboard_key == event.unicode and not button.is_pressed:
                                button.is_pressed = True
                                self.emit_midi_event(button.note, 100)

                        elif event.type == pygame.KEYUP:
                            if button.keyboard_key == event.unicode and button.is_pressed:
                                button.is_pressed = False
                                self.emit_midi_event(button.note, 0)

            # Draw interface
            self.screen.fill((255, 255, 255))
            
            # Draw piano grid
            for button in self.buttons:
                cmul = 0.5 if button.is_pressed else 1
                pygame.draw.rect(self.screen, tuple(int(c*cmul) for c in button.color), button.rect)
                pygame.draw.rect(self.screen, (0, 0, 0), button.rect, 2)
                
                # Draw note label
                text = self.font.render(button.label, True, (0, 0, 0))
                text_rect = text.get_rect(center=button.rect.center)
                self.screen.blit(text, text_rect)
            
            # pygame.draw.rect(self.screen, (100, 200, 100), self.save_button)
            # font = pygame.font.Font(None, 36)
            # text = font.render("Save", True, (0, 0, 0))
            # text_rect = text.get_rect(center=self.save_button.center)
            # self.screen.blit(text, text_rect)
            
            midi_buffer.render(self.screen, pygame.Rect(20, 580, 1018, 200), time.time())


            pygame.display.flip()

        self.midi_device.cleanup()
        pygame.midi.quit()
        pygame.quit()


def enumerate_midi_devices():
    # Initialize MIDI input and output interfaces
    midi_out = rtmidi.MidiOut()

    try:
        output_ports = midi_out.get_ports()

        # Print available output ports
        print("\nAvailable MIDI output ports:")
        for i, port in enumerate(output_ports):
            print(f"{i}: {port}")

    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        # Close the MIDI interfaces
        midi_out.close_port()
        del midi_out



def main():
    parser = argparse.ArgumentParser(description='MIDI Piano')
    parser.add_argument('--output-device', type=str, help='MIDI device name (partial match)')
    args = parser.parse_args()

    # Call the function to enumerate MIDI devices
    enumerate_midi_devices()
    try:
        midi_device = MidiDevice(args.output_device)
        midi_buffer = MidiBuffer()
        piano = MidiPiano(midi_device)
        
        # Connect buffer to piano events
        piano.add_event_handler(midi_buffer.add_event)
        
        piano.run(midi_buffer)
        
    except ValueError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()