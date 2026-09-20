import shutil
from pathlib import Path

# Set this to the parent directory containing the numbered folders
base_path = Path("joint_cond") 

for subfolder in base_path.iterdir():
    if subfolder.is_dir():
        # Target only .wav files within the current subfolder
        wav_files = list(subfolder.glob("*.wav"))
        
        if wav_files:
            # Create the 'full' child directory
            target_dir = subfolder / "full"
            target_dir.mkdir(exist_ok=True)
            
            # Move each audio file into the new directory
            for wav_file in wav_files:
                shutil.move(wav_file, target_dir / wav_file.name)
                print(f"Moved {wav_file.name} to {target_dir}")