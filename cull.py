import os
import shutil
import argparse
import re

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="initial culling of files logs as prometheus metrics.")
    parser.add_argument("--max_rmsac", type=float, help="maximum rmsac to keep (not inclusive, this value is rejected)")
    parser.add_argument("--rejectdir", type=str, help="directory to put all rejected images into (relative dir struture is preserved)")
    
    # treat args parsed as a dictionary
    args = vars(parser.parse_args())

    user_rmsac_max = 1.0
    if "max_rmsac" in args and args["max_rmsac"] is not None:
        user_rmsac_max = float(args["max_rmsac"])

    user_rejectdir = args["rejectdir"]

    r_stars = re.compile(".*STARS_([0-9]+)[^0-9].*")
    r_rmsac = re.compile(".*RMSAC_([.0-9]+)[^.0-9].*")

    for dirpath, _, _ in os.walk(f".{os.sep}"):
        found = {
            "stars_max": 0,
            "stars_min": 99999999,
            "rmsac_max": 0,
            "rmsac_min": 99999999,
        }
        images_found = False
        for filename in os.listdir(dirpath):
            if "fits" in filename:
                images_found = True

                m_stars = r_stars.match(filename)
                stars = int(m_stars.group(1))
                if stars > found["stars_max"]:
                    found["stars_max"] = stars
                if stars < found["stars_min"]:
                    found["stars_min"] = stars

                m_rmsac = r_rmsac.match(filename)
                rmsac = float(m_rmsac.group(1))
                if rmsac > found["rmsac_max"]:
                    found["rmsac_max"] = rmsac
                if rmsac < found["rmsac_min"]:
                    found["rmsac_min"] = rmsac
        if images_found:
            print("==============================")
            print(f"Images found in '{dirpath}'.")
            print(f"RMSAC values: min={found['rmsac_min']}, max={found['rmsac_max']}")
            print(f"Star counts:  min={found['stars_min']}, max={found['stars_max']}")
            user_stars_min = input("Minimum stars to keep: ")

            if user_stars_min is None or user_stars_min == "":
                user_stars_min = 0
            else:
                user_stars_min = int(user_stars_min)

            reject_count = 0
            for filename in os.listdir(dirpath):
                if "fits" in filename:
                    reject_image = False
                    m_stars = r_stars.match(filename)
                    stars = int(m_stars.group(1))
                    if stars < user_stars_min:
                        reject_image = True

                    m_rmsac = r_rmsac.match(filename)
                    rmsac = float(m_rmsac.group(1))
                    if rmsac > user_rmsac_max:
                        reject_image = True

                    if reject_image:
                        reject_count += 1
                        # create target directory
                        os.makedirs(os.path.join(user_rejectdir, dirpath), exist_ok=True)
                        # move the file
                        shutil.move(os.path.join(dirpath, filename), os.path.join(user_rejectdir, dirpath, filename))
            print("------------------------------")
            print(f"Rejected file count: {reject_count}")
            print("==============================")