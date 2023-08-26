import os
from pyopta.pass_matrix import PassMatrix

script_dir = os.path.dirname(__file__)

PATH_PASS_MATRIX = f"{script_dir}/f27_passmatrix_sfc/"
PATH_PASS_MATRIX_PNG = f"{script_dir}/f27_passmatrix_sfc_pngs/"

def main():
    print("Creating pass matrices...")
    for filename in os.listdir(PATH_PASS_MATRIX):
        file_pm = os.path.join(PATH_PASS_MATRIX, filename)
        opta_f27 = PassMatrix(file_pm)
        pitch_pm = opta_f27.get_pitch_pass_matrix(team_color='#F43333')
        output_name = os.path.splitext(f"{filename}")[0]+'.png'
        output_path = f"{PATH_PASS_MATRIX_PNG}{output_name}"
        print(f"Saving {output_path}...")
        pitch_pm.savefig(output_path)

if __name__ == "__main__":
    main()
