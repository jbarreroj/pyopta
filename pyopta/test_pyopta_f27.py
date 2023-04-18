import os
from pass_matrix import PassMatrix

script_dir = os.path.dirname(__file__)

PATH_F27_T1 = f"{script_dir}/docs/pass_matrix_23_2021_g2219395_t181.xml"
PATH_F27_T2 = f"{script_dir}/docs/pass_matrix_23_2021_g2219395_t184.xml"

print(f"Parsing {PATH_F27_T1}")
opta_f27 = PassMatrix(PATH_F27_T1)
print(f"Parsing {PATH_F27_T2}")
opta_f27_2 = PassMatrix(PATH_F27_T2)

print("PRINTING PASS_MATRIX DATAFRAME (1)")
print("------------------")
print(opta_f27.get_df_pass_matrix())
print("------------------")

print("PRINTING PASS_MATRIX DATAFRAME (2)")
print("------------------")
print(opta_f27_2.get_df_pass_matrix())
print("------------------")

pm_pitch1 = opta_f27.get_pitch_pass_matrix(min_passes=3, team_color='#ff0000')
pm_pitch2 = opta_f27_2.get_pitch_pass_matrix(min_passes=3, team_color='#0000ff', with_subs=True)
pm_pitch1.show()