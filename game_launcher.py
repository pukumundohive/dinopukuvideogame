#!/usr/bin/env python3
"""
Game Launcher - A utility script to launch the dinopukuvideojuego.py game
This script ensures all dependencies are installed and the game runs properly
"""
import os
import sys
import subprocess
import platform


def check_pygame_installed():
    """Check if Pygame is installed, and install it if not."""
    try:
        import pygame
        print(f"✓ Pygame {pygame.version.ver} is already installed.")
        return True
    except ImportError:
        print("Pygame is not installed. Attempting to install...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"])
            print("✓ Pygame has been successfully installed.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to install Pygame: {e}")
            print("Please try installing Pygame manually using:")
            print("pip install pygame")
            return False


def check_game_file_exists():
    """Check if the game file exists in the current directory."""
    game_file = "dinopukuvideojuego.py"
    if os.path.isfile(game_file):
        print(f"✓ Game file '{game_file}' found.")
        return True
    else:
        print(f"Error: Game file '{game_file}' not found in the current directory.")
        print(f"Make sure '{game_file}' is in the same directory as this launcher.")
        return False


def run_game():
    """Run the game with appropriate environment settings."""
    game_file = "dinopukuvideojuego.py"
    
    # Set SDL environment variables for better compatibility
    os.environ["SDL_VIDEO_CENTERED"] = "1"  # Center the game window
    
    # Handle platform-specific settings
    system = platform.system()
    if system == "Linux":
        # Some Linux-specific settings to improve performance
        os.environ["SDL_AUDIODRIVER"] = "pulseaudio"
    elif system == "Darwin":  # macOS
        os.environ["SDL_AUDIODRIVER"] = "coreaudio"
    
    # Run the game
    print(f"Launching {game_file}...")
    try:
        if os.access(game_file, os.X_OK):
            # If the file is executable, run it directly
            subprocess.run(["./" + game_file])
        else:
            # Otherwise use Python to run it
            subprocess.run([sys.executable, game_file])
        print("Game finished.")
        return True
    except Exception as e:
        print(f"Error running the game: {e}")
        return False


def check_additional_dependencies():
    """Check for any additional dependencies that might be needed."""
    try:
        # These are common dependencies that Pygame might need
        import numpy
        print("✓ NumPy is installed (might be required by some Pygame components).")
    except ImportError:
        print("Note: NumPy is not installed. Some Pygame features might require it.")
        print("If you experience issues, you can install it with: pip install numpy")
    
    return True


def main():
    """Main function to run the launcher checks and start the game."""
    print("=== Dino Puku Game Launcher ===")
    
    # Check if the game file exists
    if not check_game_file_exists():
        return False
    
    # Check and install Pygame if needed
    if not check_pygame_installed():
        return False
    
    # Check additional dependencies
    check_additional_dependencies()
    
    # Run the game
    print("\nStarting the game...")
    success = run_game()
    
    return success


if __name__ == "__main__":
    success = main()
    if not success:
        print("\nThere was an issue running the game. Please check the errors above.")
        sys.exit(1)
    sys.exit(0)
