import os
from pyopta.match_results import MatchResults

script_dir = os.path.dirname(__file__)

PATH_EVENTS_VCF_AWAY = f"{script_dir}/f9_matchresults_vcf_away/"
PATH_EVENTS_VCF_AWAY_CSV = f"{script_dir}/f9_matchresults_vcf_away_csv/"

def main():
    print("Obtaining dataframe stats - successful_final_third_passes...")
    for filename in os.listdir(PATH_EVENTS_VCF_AWAY):
        file_mr = os.path.join(PATH_EVENTS_VCF_AWAY, filename)
        opta_f9 = MatchResults(file_mr)
        df = opta_f9.get_df_specific_stat('successful_final_third_passes', team_id = 191)
        output_name = os.path.splitext(f"{filename}")[0]+'.csv'
        output_path = f"{PATH_EVENTS_VCF_AWAY_CSV}{output_name}"
        print(f"Saving {output_path}...")
        df.to_csv(output_path, index=False)

if __name__ == "__main__":
    main()
