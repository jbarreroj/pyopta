import os
from pyopta.events import Events

script_dir = os.path.dirname(__file__)

PATH_EVENTS_RSO_HOME = f"{script_dir}/f24_events_rso_home/"
PATH_EVENTS_RSO_HOME_PNG = f"{script_dir}/f24_events_rso_home_pngs/"

def main():
    print("Creating pngs from corners events...")
    for filename in os.listdir(PATH_EVENTS_RSO_HOME):
        file_ev = os.path.join(PATH_EVENTS_RSO_HOME, filename)
        opta_f24 = Events(file_ev)
        pitch_corner = opta_f24.get_pitch_corners(team_id = 188)
        output_name = os.path.splitext(f"{filename}")[0]+'.png'
        output_path = f"{PATH_EVENTS_RSO_HOME_PNG}{output_name}"
        print(f"Saving {output_path}...")
        pitch_corner.savefig(output_path)

if __name__ == "__main__":
    main()
